# gdpr/sticky_policies.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Set, Optional, Dict


@dataclass
class StickyPolicy:
    """
    Sticky Policy (SP) asociada a un dato personal.
    Se reconstruye a partir de la traza.
    """

    # Identidad del dato
    data_id: str

    owner: Optional[str] = None
    controller: Optional[str] = None

    # Autorizaciones principales
    purposes: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)

    # Consentimiento
    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None
    consent_expired: bool = False
    consent_expiration_timestamp: Optional[datetime] = None

    # Retención
    max_retention_time: Optional[datetime] = None

    # Obligaciones (ej. logging)
    obligations: Set[str] = field(default_factory=set)

    # 🔹 TERCEROS
    # Cada tercero tiene una "mini-SP" derivada
    # {
    #   "ThirdPartyA": {
    #       "purposes": {...},
    #       "permissions": {...},
    #       "retention_days": int | None,
    #       "shared_at": datetime,
    #       "active": bool
    #   }
    # }
    third_parties: Dict[str, dict] = field(default_factory=dict)

    # Estados especiales
    processing_restricted: bool = False
    erased: bool = False
    erasure_timestamp: Optional[datetime] = None

    # Historial de accesos
    access_history: List[dict] = field(default_factory=list)


def build_sticky_policy_from_trace(trace) -> StickyPolicy:
    """
    Reconstruye la Sticky Policy a partir de una traza GDPR-enriquecida.
    """
    sp = StickyPolicy(
        data_id=trace.attributes.get("concept:name", "unknown")
    )

    for event in trace:
        name = event["concept:name"]
        ts = event["time:timestamp"]

        # =====================================================
        # CONSENTIMIENTO
        # =====================================================
        if name == "gdpr:giveConsent":
            sp.consent_given = True
            sp.consent_timestamp = ts
            sp.purposes.add(event.get("gdpr:purpose", "unspecified"))
            sp.obligations.add("log_access")

            max_days = event.get("gdpr:max_time_days")
            if max_days:
                sp.consent_expiration_timestamp = ts + timedelta(days=max_days)

        elif name == "gdpr:consentExpired":
            sp.consent_expired = True
            sp.consent_expiration_timestamp = ts

        # =====================================================
        # RESTRICCIÓN DE TRATAMIENTO
        # =====================================================
        if name == "gdpr:restrictProcessing":
            sp.processing_restricted = True

        elif name == "gdpr:liftRestriction":
            sp.processing_restricted = False

        # =====================================================
        # BORRADO
        # =====================================================
        if name == "gdpr:eraseData":
            sp.erased = True
            sp.erasure_timestamp = ts

        # =====================================================
        # TERCEROS
        # =====================================================

        if name == "gdpr:shareDataWithThirdParty":
            tp_name = event.get("gdpr:third_party")
            if not tp_name:
                continue

            sp.third_parties[tp_name] = {
                "role": event.get("gdpr:role", "processor"),
                "purposes": {event.get("gdpr:purpose", "unspecified")},
                "active": True,
                "shared_timestamp": event["time:timestamp"]
            }

        if name == "gdpr:revokeThirdPartyAccess":
            tp_name = event.get("gdpr:third_party")
            if tp_name in sp.third_parties:
                sp.third_parties[tp_name]["active"] = False

        # =====================================================
        # ACCESOS
        # =====================================================
        if event.get("gdpr:access"):
            sp.permissions.add(event["gdpr:access"])
            sp.access_history.append({
                "timestamp": ts,
                "access": event["gdpr:access"],
                "purpose": event.get("gdpr:purpose"),
                "actor": event.get("gdpr:actor"),
                "activity": name
            })

    return sp
