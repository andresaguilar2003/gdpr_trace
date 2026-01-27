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
                "blocking": True,  
                "message": "Uso de datos para un propósito no autorizado",
                "events": [e]
            })

    return violations


def validate_access_without_permission(trace):
    violations = []
    consent_active = False
    processing_restricted = False

    for event in trace:
        name = event["concept:name"]

        if name == "gdpr:permissionGranted":
            consent_active = True

        elif name in {"gdpr:withdrawConsent", "gdpr:consentExpired"}:
            consent_active = False

        elif name == "gdpr:restrictProcessing":
            processing_restricted = True

        elif name == "gdpr:liftRestriction":
            processing_restricted = False

        elif event.get("gdpr:access"):
            if not consent_active:
                violations.append({
                    "type": "access_without_consent",
                    "severity": "high",
                    "blocking": True,
                    "message": "Acceso a datos sin consentimiento activo",
                    "events": [event]
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