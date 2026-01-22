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