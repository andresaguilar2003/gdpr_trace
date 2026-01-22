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


def validate_data_minimization(trace):
    violations = []

    for e in trace:
        if e.get("gdpr:access") and e.get("gdpr:data_scope") == "excessive":
            violations.append({
                "type": "data_minimization_violation",
                "severity": "medium",
                "message": "Acceso a más datos de los necesarios",
                "events": [e]
            })

    return violations

def validate_purpose_limitation(trace):
    violations = []

    allowed_purpose = trace.attributes.get("gdpr:default_purpose")

    for e in trace:
        if e.get("gdpr:access") and e.get("gdpr:purpose") != allowed_purpose:
            violations.append({
                "type": "purpose_violation",
                "severity": "high",
                "message": "Uso de datos para un propósito no autorizado",
                "events": [e]
            })

    return violations

def validate_access_without_permission(trace):
    violations = []

    for i, e in enumerate(trace):
        if not e.get("gdpr:access"):
            continue

        if i == 0:
            violations.append({
                "type": "access_without_permission",
                "severity": "high",
                "message": "Acceso a datos sin autorización explícita",
                "events": [e]
            })
            continue

        prev_event = trace[i - 1]

        if prev_event["concept:name"] != "gdpr:permissionGranted":
            violations.append({
                "type": "access_without_permission",
                "severity": "high",
                "message": "Acceso a datos sin evento permissionGranted previo",
                "events": [e]
            })

    return violations


def validate_missing_access_log(trace):
    violations = []

    access_events = [
        e for e in trace if e.get("gdpr:access")
    ]

    access_logs = [
        e for e in trace
        if e["concept:name"] == GDPR_EVENTS["ACCESS_LOG"]
    ]

    for access in access_events:
        ts = access["time:timestamp"]

        matching_logs = [
            log for log in access_logs
            if log["time:timestamp"] >= ts
            and log.get("gdpr:related_activity") == access["concept:name"]
        ]

        if not matching_logs:
            violations.append({
                "type": "missing_access_log",
                "severity": "medium",
                "message": "Acceso a datos sin registro en accessLog",
                "events": [access]
            })

    return violations