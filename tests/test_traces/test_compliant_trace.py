from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.validators.validators import validate_trace
from gdpr.generators import print_violations_summary

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

import copy

def test_inspect_compliant_trace():
    log = load_event_log("data/input/test/log_long_case.xes")

    original = copy.deepcopy(log[0])
    compliant = build_compliant_trace(copy.deepcopy(log[0]))

    print_trace(original, "ORIGINAL TRACE")
    print_trace(compliant, "GDPR-COMPLIANT TRACE")

    violations = validate_trace(compliant)
    print_violations_summary(violations)

    assert len(compliant) > len(original)

