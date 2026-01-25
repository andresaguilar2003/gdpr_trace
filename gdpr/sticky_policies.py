# gdpr/sticky_policies.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Set, Optional, Dict


@dataclass
class StickyPolicy:
    """
    Sticky Policy (SP) asociada a un dato personal.
    Evidencia normativa reconstruida a partir de la traza.
    """

    # Identidad del dato
    data_id: str
    owner: Optional[str] = None
    controller: Optional[str] = None

    # Autorizaciones globales
    purposes: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)

    # Consentimiento
    consent_given: bool = False
    consent_timestamp: Optional[datetime] = None
    consent_expired: bool = False
    consent_expiration_timestamp: Optional[datetime] = None

    # Retención global
    max_retention_time: Optional[datetime] = None

    # Obligaciones
    obligations: Set[str] = field(default_factory=set)

    # 🔹 TERCEROS (mini-Sticky Policies)
    third_parties: Dict[str, dict] = field(default_factory=dict)

    # Estados especiales
    processing_restricted: bool = False
    erased: bool = False
    erasure_timestamp: Optional[datetime] = None

    # Historial
    access_history: List[dict] = field(default_factory=list)


# ============================================================
# BUILDER
# ============================================================

def build_sticky_policy_from_trace(trace) -> StickyPolicy:
    sp = StickyPolicy(
        data_id=trace.attributes.get("concept:name", "unknown")
    )

    for event in trace:
        name = event["concept:name"]
        ts = event["time:timestamp"]

        # ----------------------------------------------------
        # CONSENTIMIENTO
        # ----------------------------------------------------
        if name == "gdpr:giveConsent":
            sp.consent_given = True
            sp.consent_timestamp = ts
            sp.purposes.add(event.get("gdpr:purpose", "unspecified"))
            sp.obligations.add("log_access")

            max_days = event.get("gdpr:max_time_days")
            if max_days:
                sp.consent_expiration_timestamp = ts + timedelta(days=max_days)
                sp.max_retention_time = sp.consent_expiration_timestamp

        elif name == "gdpr:consentExpired":
            sp.consent_expired = True
            sp.consent_expiration_timestamp = ts

        # ----------------------------------------------------
        # RESTRICCIÓN
        # ----------------------------------------------------
        if name == "gdpr:restrictProcessing":
            sp.processing_restricted = True

        elif name == "gdpr:liftRestriction":
            sp.processing_restricted = False

        # ----------------------------------------------------
        # BORRADO
        # ----------------------------------------------------
        if name == "gdpr:eraseData":
            sp.erased = True
            sp.erasure_timestamp = ts

            # Propagación normativa (Art. 19)
            for tp in sp.third_parties.values():
                tp["notified_of_erasure"] = True
                tp["active"] = False

        # ----------------------------------------------------
        # TERCEROS
        # ----------------------------------------------------
        if name == "gdpr:shareDataWithThirdParty":
            tp_name = event.get("gdpr:third_party")
            if not tp_name:
                continue

            retention_days = event.get("gdpr:retention_days")
            retention_until = (
                ts + timedelta(days=retention_days)
                if retention_days else None
            )

            tp = sp.third_parties.setdefault(tp_name, {
                "role": event.get("gdpr:role", "processor"),
                "purposes": set(),
                "permissions": set(),
                "active": True,
                "shared_timestamp": ts,
                "retention_until": retention_until,
                "country": event.get("gdpr:country"),
                "transfer_mechanism": event.get("gdpr:transfer_mechanism"),
                "legal_basis": event.get("gdpr:legal_basis"),
                "own_legal_basis": event.get("gdpr:own_legal_basis", False),
                "notified_of_erasure": False,
            })

            tp["purposes"].add(event.get("gdpr:purpose", "unspecified"))
            if event.get("gdpr:access"):
                tp["permissions"].add(event["gdpr:access"])

        elif name == "gdpr:revokeThirdPartyAccess":
            tp_name = event.get("gdpr:third_party")
            if tp_name in sp.third_parties:
                sp.third_parties[tp_name]["active"] = False

        # ----------------------------------------------------
        # ACCESOS
        # ----------------------------------------------------
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
