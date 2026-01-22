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
