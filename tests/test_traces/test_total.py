from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace, build_non_compliant_trace
from gdpr.validators.validators import validate_trace
from gdpr.generators import print_violations_summary
import copy


def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} | "
            f"gdpr:event={e.get('gdpr:event', False)} | "
            f"operation={e.get('gdpr:operation')} | "
            f"access_type={e.get('gdpr:access_type')} | "
        )



def test_full_gdpr_pipeline_inspection():
    log = load_event_log("data/input/test/log_long_case.xes")

    # =====================================================
    # 1️⃣ TRAZA ORIGINAL (SIN GDPR)
    # =====================================================
    original = copy.deepcopy(log[0])
    print_trace(original, "ORIGINAL TRACE (NO GDPR)")

    # =====================================================
    # 2️⃣ TRAZA GDPR-COMPLIANT
    # =====================================================
    compliant = build_compliant_trace(copy.deepcopy(log[0]))
    print_trace(compliant, "GDPR-COMPLIANT TRACE")

    compliant_violations = validate_trace(compliant)

    print("\nViolations detected in COMPLIANT trace:")
    if compliant_violations:
        print_violations_summary(compliant_violations)
    else:
        print("✅ No violations detected (ideal compliant case)")

    # Assert estructural
    assert len(compliant) > len(original)
    assert compliant.attributes["gdpr:compliance"] == "compliant"

    # =====================================================
    # 3️⃣ TRAZAS GDPR NON-COMPLIANT (x3)
    # =====================================================
    non_compliant_traces = [
        build_non_compliant_trace(compliant)
        for _ in range(3)
    ]

    for idx, nc in enumerate(non_compliant_traces, start=1):
        print_trace(nc, f"GDPR NON-COMPLIANT TRACE #{idx}")

        violations = validate_trace(nc)

        print("\nViolations detected:")
        if violations:
            print_violations_summary(violations)
        else:
            print("⚠️ No detectable violations in this run (expected behavior)")

        # Assert robusto (no depende del azar)
        assert nc.attributes["gdpr:compliance"] == "non_compliant"

        print("\n" + "-" * 60)
