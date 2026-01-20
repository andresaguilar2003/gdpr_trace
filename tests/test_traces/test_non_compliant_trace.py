from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace, build_non_compliant_trace
from gdpr.validators import validate_trace

def print_trace(trace, title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['time:timestamp']} | {e['concept:name']} | "
            f"gdpr:event={e.get('gdpr:event', False)} | "
            f"access={e.get('gdpr:access')} | "
            f"violation={e.get('gdpr:violation')}"
        )

def test_inspect_non_compliant_trace():
    log = load_event_log("data/input/log_original.xes")
    trace = log[0]

    compliant = build_compliant_trace(trace)
    non_compliant = build_non_compliant_trace(compliant)

    print_trace(compliant, "GDPR-COMPLIANT TRACE")
    print_trace(non_compliant, "GDPR NON-COMPLIANT TRACE")

    violations = validate_trace(non_compliant)

    print("\nViolations detected:")
    for v in violations:
        print(f"- {v['type']} | severity={v['severity']} | {v['message']}")

    # Afirmaciones clave
    assert len(violations) > 0

    diff_traces(compliant, non_compliant)


def diff_traces(trace_a, trace_b):
    print("\nDIFERENCIAS ENTRE TRAZAS:")
    for i, (e1, e2) in enumerate(zip(trace_a, trace_b)):
        diffs = []
        for key in set(e1.keys()).union(e2.keys()):
            if e1.get(key) != e2.get(key):
                diffs.append(f"{key}: {e1.get(key)} → {e2.get(key)}")

        if diffs:
            print(f"\nEvento {i}: {e1['concept:name']}")
            for d in diffs:
                print("  -", d)

