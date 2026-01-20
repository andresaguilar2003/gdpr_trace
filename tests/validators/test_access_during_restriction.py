from datetime import timedelta
from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.validators import validate_trace

def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} "
            f"| access={e.get('gdpr:access')} | violation={e.get('gdpr:violation')}"
        )

def test_access_during_restriction():
    log = load_event_log("data/input/log_original.xes")
    trace = build_compliant_trace(log[0])

    restriction_start = trace[-1]["time:timestamp"] + timedelta(seconds=1)

    restrict_event = {
        "concept:name": "gdpr:restrictProcessing",
        "time:timestamp": restriction_start,
        "gdpr:event": True,
        "gdpr:actor": "Controller"
    }

    illegal_access = {
        "concept:name": "access_medical_record",
        "time:timestamp": restriction_start + timedelta(minutes=5),
        "gdpr:access": "gdpr:readData",
        "gdpr:actor": "Controller",
        "gdpr:purpose": "medical_treatment"
    }

    lift_event = {
        "concept:name": "gdpr:liftRestriction",
        "time:timestamp": restriction_start + timedelta(minutes=10),
        "gdpr:event": True,
        "gdpr:actor": "Controller"
    }

    trace.append(restrict_event)
    trace.append(illegal_access)
    trace.append(lift_event)


    print_trace(trace, "TRACE WITH ACCESS DURING RESTRICTION")

    violations = validate_trace(trace)

    print("\nViolations detected:")
    for v in violations:
        print(f"- {v['type']} | severity={v['severity']} | {v['message']}")

    assert any(v["type"] == "access_during_restriction" for v in violations)
