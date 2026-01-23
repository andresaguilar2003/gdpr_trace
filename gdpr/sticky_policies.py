# gdpr/sticky_policies.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Set, Optional


@dataclass
class StickyPolicy:
    """
    Sticky Policy (SP) asociada a un dato personal.
    Se reconstruye a partir de la traza.
    """
    data_id: str

    owner: Optional[str] = None
    controller: Optional[str] = None

    purposes: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)

    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None
    consent_expired: bool = False
    max_retention_time: Optional[datetime] = None
    consent_expiration_timestamp: Optional[datetime] = None

    obligations: Set[str] = field(default_factory=set)


    processing_restricted: bool = False
    erased: bool = False
    erasure_timestamp: Optional[datetime] = None

    access_history: List[dict] = field(default_factory=list)

def build_sticky_policy_from_trace(trace) -> StickyPolicy:
    """
    Reconstruye la Sticky Policy a partir de una traza GDPR-enriquecida.
    """
    sp = StickyPolicy(data_id=trace.attributes.get("concept:name", "unknown"))

    for event in trace:
        name = event["concept:name"]

        # Consentimiento
        if name == "gdpr:giveConsent":
            sp.consent_given = True
            sp.consent_timestamp = event["time:timestamp"]
            sp.purposes.add(event.get("gdpr:purpose", "unspecified"))
            sp.obligations.add("log_access")

            max_days = event.get("gdpr:max_time_days")
            if max_days:
                sp.consent_expiration_timestamp = (
                    sp.consent_timestamp + timedelta(days=max_days)
                )


        elif name == "gdpr:consentExpired":
            sp.consent_expiration_timestamp = event["time:timestamp"]


        # Restricción de tratamiento
        if name == "gdpr:restrictProcessing":
            sp.processing_restricted = True

        if name == "gdpr:liftRestriction":
            sp.processing_restricted = False

        # Borrado de datos
        if name == "gdpr:eraseData":
            sp.erased = True
            sp.erasure_timestamp = event["time:timestamp"]


        # Accesos a datos
        if event.get("gdpr:access"):
            sp.permissions.add(event["gdpr:access"])
            sp.access_history.append({
                "timestamp": event["time:timestamp"],
                "access": event["gdpr:access"],
                "purpose": event.get("gdpr:purpose"),
                "actor": event.get("gdpr:actor"),
                "activity": name
            })

    return sp
