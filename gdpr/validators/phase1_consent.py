from datetime import timedelta
from gdpr.vocabulary import GDPR_EVENTS


# ============================================================
# HELPERS
# ============================================================

def get_events(trace, event_name):
    return [
        e for e in trace
        if e["concept:name"] == event_name
    ]



def validate_consent_before_access(trace):
    violations = []

    consent_events = get_events(trace, GDPR_EVENTS["CONSENT"])
    access_events = [e for e in trace if e.get("gdpr:access")]

    # ❌ Accesos sin ningún consentimiento
    if not consent_events and access_events:
        violations.append({
            "type": "missing_consent",
            "severity": "high",
            "message": "Hay accesos a datos personales sin consentimiento previo",
            "events": access_events
        })
        return violations

    # ✅ Si no hay accesos, no hay violación
    if not access_events:
        return violations
    
    # ❌ Accesos antes del consentimiento
    consent_ts = consent_events[0]["time:timestamp"]

    for access in access_events:
        if access["time:timestamp"] < consent_ts:
            violations.append({
                "type": "consent_after_access",
                "severity": "high",
                "message": "Acceso a datos antes de obtener el consentimiento",
                "events": [access]
            })

    return violations


def validate_implicit_consent(trace):
    violations = []

    for e in get_events(trace, GDPR_EVENTS["CONSENT"]):
        consent_type = e.get("gdpr:consent_type", "implicit")

        if consent_type != "explicit":
            violations.append({
                "type": "implicit_consent",
                "severity": "medium",
                "message": "El consentimiento no fue explícito",
                "events": [e]
            })

    return violations

