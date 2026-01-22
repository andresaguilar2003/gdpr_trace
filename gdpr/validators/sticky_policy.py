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


def validate_sticky_policy(trace):
    violations = []

    sp = trace.attributes.get("gdpr:sticky_policy")
    if not sp:
        return violations

    for e in trace:
        if not e.get("gdpr:access"):
            continue

        if sp.erased:
            violations.append({
                "type": "sp_access_after_erasure",
                "severity": "critical",
                "message": "La Sticky Policy indica datos borrados pero hay accesos",
                "events": [e]
            })

        if sp.processing_restricted:
            violations.append({
                "type": "sp_access_during_restriction",
                "severity": "high",
                "message": "Acceso prohibido según la Sticky Policy",
                "events": [e]
            })

        if sp.consent_expired:
            violations.append({
                "type": "sp_access_after_consent_expiration",
                "severity": "high",
                "message": "Acceso prohibido por expiración de consentimiento en la SP",
                "events": [e]
            })

    return violations