from datetime import timedelta
from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.validators.validators import validate_trace
from gdpr.vocabulary import GDPR_EVENTS


def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} "
            f"| access={e.get('gdpr:access')} | violation={e.get('gdpr:violation')}"
        )

def test_late_breach_notification():
    log = load_event_log("data/input/log_original.xes")
    trace = build_compliant_trace(log[0])

    breach_time = trace[-1]["time:timestamp"] + timedelta(minutes=1)

    breach_event = {
        "concept:name": GDPR_EVENTS["BREACH"],
        "time:timestamp": breach_time,
        "gdpr:event": True,
        "gdpr:actor": "Controller"
    }

    late_notification = {
        "concept:name": GDPR_EVENTS["NOTIFY_BREACH"],
        "time:timestamp": breach_time + timedelta(hours=100),  # >72h
        "gdpr:event": True,
        "gdpr:actor": "Controller"
    }

    trace.append(breach_event)
    trace.append(late_notification)

    print_trace(trace, "TRACE WITH LATE BREACH NOTIFICATION")

    violations = validate_trace(trace)

    print("\nViolations detected:")
    for v in violations:
        print(f"- {v['type']} | severity={v['severity']} | {v['message']}")

    assert any(v["type"] == "late_breach_notification" for v in violations)
