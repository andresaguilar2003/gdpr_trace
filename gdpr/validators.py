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


def annotate_violations_on_trace(trace, violations):
    """
    Marca los eventos de la traza que causan violaciones GDPR.
    """
    for v in violations:
        for event in v.get("events", []):
            event["gdpr:violation"] = v["type"]
            event["gdpr:violation_severity"] = v.get("severity", "unknown")
            event["gdpr:violation_message"] = v.get("message")


# ============================================================
# VALIDATORS
# ============================================================

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


def validate_breach_notification_time(trace):
    violations = []

    detects = get_events(trace, GDPR_EVENTS["BREACH"])
    notifies = get_events(trace, GDPR_EVENTS["NOTIFY_BREACH"])

    for detect in detects:
        detect_ts = detect["time:timestamp"]

        related_notify = [
            n for n in notifies
            if n["time:timestamp"] > detect_ts
        ]

        # ❌ No se notificó
        if not related_notify:
            violations.append({
                "type": "missing_breach_notification",
                "severity": "critical",
                "message": "Brecha detectada sin notificación",
                "events": [detect]
            })
            continue

        notify = related_notify[0]
        notify_ts = notify["time:timestamp"]

        # ❌ Notificación tardía (>72h)
        if notify_ts > detect_ts + timedelta(hours=72):
            violations.append({
                "type": "late_breach_notification",
                "severity": "critical",
                "message": "Notificación de brecha fuera de las 72 horas legales",
                "events": [detect, notify]
            })

    return violations


def validate_data_subject_rights(trace):
    violations = []

    requests = get_events(trace, GDPR_EVENTS["REQUEST_INFO"])
    responses = get_events(trace, GDPR_EVENTS["PROVIDE_INFO"])

    for req in requests:
        req_ts = req["time:timestamp"]

        matching_responses = [
            r for r in responses
            if r["time:timestamp"] > req_ts
        ]

        # ❌ Sin respuesta
        if not matching_responses:
            violations.append({
                "type": "missing_right_response",
                "severity": "medium",
                "message": "Solicitud de información sin respuesta",
                "events": [req]
            })
            continue

        response = matching_responses[0]
        response_ts = response["time:timestamp"]

        # ❌ Respuesta fuera de plazo (>30 días)
        if response_ts > req_ts + timedelta(days=30):
            violations.append({
                "type": "late_right_response",
                "severity": "medium",
                "message": "Respuesta a derechos fuera del plazo legal (30 días)",
                "events": [req, response]
            })

    return violations


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
            violations.append({
                "type": "access_during_restriction",
                "severity": "high",
                "message": "Acceso a datos mientras el tratamiento estaba restringido",
                "events": [event]
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


# ============================================================
# MAIN VALIDATION ENTRY POINT
# ============================================================

def validate_trace(trace):
    violations = []

    violations.extend(validate_consent_before_access(trace))
    violations.extend(validate_withdrawn_consent(trace))
    violations.extend(validate_processing_restriction(trace))
    violations.extend(validate_breach_notification_time(trace))
    violations.extend(validate_data_subject_rights(trace))
    violations.extend(validate_erase_without_processing(trace))

    return violations
