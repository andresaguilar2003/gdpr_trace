# tests/non_compliant/test_temporal_consistency_non_compliant.py

import pytest

from gdpr.importers import load_event_log
from gdpr.pipelines import build_non_compliant_trace
from gdpr.validators.validators import validate_trace


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


@pytest.fixture
def non_compliant_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return build_non_compliant_trace(log[0])


def test_non_compliant_trace_is_explicitly_annotated(non_compliant_trace):
    """
    Verifica que una traza non-compliant está correctamente marcada
    y documenta explícitamente las violaciones GDPR presentes.
    """

    print_section("ANALYSING NON-COMPLIANT TRACE")

    print("TRACE ATTRIBUTES")
    for k, v in non_compliant_trace.attributes.items():
        if k.startswith("gdpr:"):
            print(f"  {k}: {v}")

    violation_types = non_compliant_trace.attributes.get("gdpr:violation_types", [])

    print("\nSUMMARY")
    print(f"Violation types declared: {violation_types}")

    # ---- Assertions ----

    assert non_compliant_trace.attributes.get("gdpr:compliance") == "non_compliant", (
        "Trace is not marked as non-compliant"
    )

    assert len(violation_types) > 0, (
        "Non-compliant trace does not declare any violation types"
    )
