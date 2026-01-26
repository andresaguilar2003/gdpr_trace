# tests/compliant/test_happy_path_full_trace.py

import pytest

from gdpr.pipelines import build_compliant_trace
from gdpr.validators.validators import validate_trace
from gdpr.sticky_policies import build_sticky_policy_from_trace
from gdpr.importers import load_event_log


@pytest.fixture
def sample_trace():
    """
    Load a real event log and return a single trace
    suitable for GDPR enrichment.
    """
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return log[0]


def test_full_compliant_trace_has_no_violations(sample_trace):
    """
    End-to-end happy path:
    - build compliant trace
    - validate it
    - expect zero GDPR violations
    """

    trace = build_compliant_trace(sample_trace)
    violations = validate_trace(trace)

    assert violations == [], (
        f"Expected no GDPR violations, found {len(violations)}: {violations}"
    )


def test_compliant_trace_contains_gdpr_context(sample_trace):
    trace = build_compliant_trace(sample_trace)

    assert trace.attributes.get("gdpr:compliance") == "compliant"
    assert "gdpr:data_controller" in trace.attributes
    assert "gdpr:data_subject" in trace.attributes


def test_compliant_trace_contains_core_gdpr_events(sample_trace):
    trace = build_compliant_trace(sample_trace)
    event_names = [e["concept:name"] for e in trace]

    assert "gdpr:giveConsent" in event_names
    assert "gdpr:accessLog" in event_names
    assert "gdpr:updateAccessHistory" in event_names



def test_sticky_policy_can_be_built_from_compliant_trace(sample_trace):
    """
    Sticky Policy reconstruction must succeed on a compliant trace.
    """

    trace = build_compliant_trace(sample_trace)
    sp = build_sticky_policy_from_trace(trace)

    assert sp is not None
    assert hasattr(sp, "permissions")
    assert len(sp.permissions) > 0
