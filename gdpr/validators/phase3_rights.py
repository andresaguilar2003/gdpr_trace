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


def validate_processing_restriction(trace):
    violations = []
    restriction_active = False

    for event in trace:
        name = event["concept:name"]

        if name == GDPR_EVENTS["RESTRICT"]:
            restriction_active = True

        elif name == GDPR_EVENTS["LIFT_RESTRICTION"]:
            restriction_active = False

        elif restriction_active and event.get("gdpr:access"):
            operation = event.get("gdpr:operation", "read")

            if operation != "read":
                violations.append({
                    "type": "access_during_restriction",
                    "severity": "high",
                    "blocking": True,
                    "message": (
                        f"Operación '{operation}' durante restricción de tratamiento"
                    ),
                    "events": [event]
                })


    return violations






def validate_erase_without_processing(trace):
    erase_events = get_events(trace, GDPR_EVENTS["ERASE"])
    access_events = [e for e in trace if e.get("gdpr:access")]

    if erase_events and not access_events:
        return [{
            "type": "erase_without_processing",
            "severity": "low",
            "message": "Se solicita borrado sin que conste tratamiento previo",
            "events": erase_events
        }]

    return []

def validate_access_after_erasure(trace):
    erase_ts = None
    violations = []

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["ERASE"]:
            erase_ts = e["time:timestamp"]

        elif erase_ts and e.get("gdpr:access"):
            violations.append({
                "type": "access_after_erasure",
                "severity": "critical",
                "blocking": True,
                "message": (
                    f"Operación '{e.get('gdpr:operation', 'unknown')}' "
                    "tras solicitud de borrado"
                ),
                "events": [e]
            })


    return violations


def validate_access_log_without_access(trace):
    violations = []

    for log in get_events(trace, GDPR_EVENTS["ACCESS_LOG"]):
        related = log.get("gdpr:related_activity")

        if not any(
            e["concept:name"] == related and e.get("gdpr:access")
            for e in trace
        ):
            violations.append({
                "type": "access_log_without_access",
                "severity": "low",
                "message": "AccessLog sin evento de acceso asociado",
                "events": [log]
            })

    return violations