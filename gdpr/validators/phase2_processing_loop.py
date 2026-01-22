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



def validate_access_after_consent_expiration(trace):
    """
    ❌ Acceso a datos personales tras la expiración del consentimiento.
    Art. 6 y 7 GDPR.
    """
    violations = []
    expired_ts = None

    for e in trace:
        name = e["concept:name"]

        if name == GDPR_EVENTS["CONSENT_EXPIRED"]:
            expired_ts = e["time:timestamp"]

        elif expired_ts and e.get("gdpr:access"):
            violations.append({
                "type": "access_after_consent_expiration",
                "severity": "high",
                "message": (
                    "Acceso a datos personales tras la expiración del consentimiento"
                ),
                "events": [e]
            })

    return violations

def validate_withdrawn_consent(trace):
    violations = []
    consent_valid = True

    for event in trace:
        name = event["concept:name"]

        if name == GDPR_EVENTS["WITHDRAW"]:
            consent_valid = False

        elif not consent_valid and event.get("gdpr:access"):
            violations.append({
                "type": "access_after_withdrawal",
                "severity": "high",
                "message": "Acceso a datos tras retirada del consentimiento",
                "events": [event]
            })

    return violations