# tests/non_compliant/test_access_without_consent.py

import pytest

from gdpr.importers import load_event_log
from gdpr.pipelines import build_non_compliant_trace


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


@pytest.fixture
def non_compliant_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return build_non_compliant_trace(log[0])


def test_access_without_prior_consent_is_flagged(non_compliant_trace):
    """
    Verifica que una traza non-compliant es marcada con una violación
    cuando el consentimiento ocurre después de un acceso implícito
    a datos personales.
    """

    trace = non_compliant_trace  # ← ya viene inyectada por pytest

    print_section("ANALYSING ACCESS WITHOUT PRIOR CONSENT")

    consent_found = False

    for e in trace:
        if e["concept:name"] == "gdpr:giveConsent":
            consent_found = True
            print(f"CONSENT | {e['time:timestamp']}")

    violation_types = trace.attributes.get(
        "gdpr:violation_types", []
    )

    print("\nSUMMARY")
    print(f"Consent present in trace: {consent_found}")
    print(f"Declared violation types: {violation_types}")

    # ---- Assertions ----

    # 1. The trace must be non-compliant due to consent timing
    assert "consent_after_access" in violation_types, (
        "Expected 'consent_after_access' violation not declared"
    )
