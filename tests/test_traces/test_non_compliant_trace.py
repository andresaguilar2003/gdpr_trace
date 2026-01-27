from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace, build_non_compliant_trace
from gdpr.validators.validators import validate_trace


def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} | "
            f"gdpr:event={e.get('gdpr:event', False)} | "
            f"access={e.get('gdpr:access')} | "
            f"violations={e.get('gdpr:violations')}"
        )


def test_inspect_multiple_non_compliant_traces():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    trace = log[0]

    # 1️⃣ Traza compliant base
    compliant = build_compliant_trace(trace)
    print_trace(compliant, "GDPR-COMPLIANT TRACE (BASE)")

    # 2️⃣ Generar 3 non-compliant desde la misma compliant
    non_compliant_traces = [
        build_non_compliant_trace(compliant)
        for _ in range(3)
    ]

    # 3️⃣ Analizar cada una
    for idx, nc in enumerate(non_compliant_traces, start=1):
        print_trace(nc, f"GDPR NON-COMPLIANT TRACE #{idx}")

        violations = validate_trace(nc)

        print("\nViolations detected:")
        if violations:
            for v in violations:
                print(f"- {v['type']} | severity={v['severity']} | {v['message']}")
        else:
            print("⚠️ No detectable violations in this run (expected behavior)")

        # ✔️ Assert estructural (no depende del azar)
        assert nc.attributes["gdpr:compliance"] == "non_compliant"

        print("\n" + "-" * 60)
