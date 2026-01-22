from gdpr.validators.validators import validate_trace
from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace, build_non_compliant_trace

def test_detect_consent_violation():
    log = load_event_log("data/input/log_original.xes")
    compliant = build_compliant_trace(log[0])
    non_compliant = build_non_compliant_trace(compliant)

    violations = validate_trace(non_compliant)

    print("\nViolaciones detectadas:")
    for v in violations:
        print(v["type"], "-", v["message"])

    assert any(v["type"] == "consent_after_access" for v in violations)
