from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.validators.validators import validate_trace
from datetime import timedelta

def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} "
            f"| access={e.get('gdpr:access')} | violation={e.get('gdpr:violation')}"
        )

def test_access_after_erasure():
    log = load_event_log("data/input/log_original.xes")
    original_trace = log[0]

    compliant = build_compliant_trace(original_trace)

    # Insertar evento de borrado
    erase_event = {
        "concept:name": "gdpr:eraseData",
        "time:timestamp": compliant[-1]["time:timestamp"] + timedelta(seconds=1),
        "gdpr:event": True,
        "gdpr:actor": "Controller",
        "gdpr:purpose": "right_to_erasure"
    }

    compliant.append(erase_event)

    # Insertar acceso ilegal posterior al borrado
    illegal_access = {
        "concept:name": "access_medical_record",
        "time:timestamp": erase_event["time:timestamp"] + timedelta(seconds=5),
        "gdpr:access": "gdpr:readData",
        "gdpr:actor": "Controller",
        "gdpr:purpose": "service_provision"
    }

    compliant.append(illegal_access)

    print_trace(compliant, "TRACE WITH ACCESS AFTER ERASURE")

    violations = validate_trace(compliant)

    print("\nViolations detected:")
    for v in violations:
        print(f"- {v['type']} | severity={v['severity']} | {v['message']}")

    # Comprobaciones clave
    assert any(v["type"] == "access_after_erasure" for v in violations)
