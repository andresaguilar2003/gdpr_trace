# tests/compliant/test_pipeline_idempotency.py

import pytest
from collections import Counter

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace


def summarize_gdpr_events(trace):
    """
    Returns a Counter with GDPR event names and their counts.
    """
    gdpr_events = [
        e["concept:name"]
        for e in trace
        if e.get("gdpr:event") is True
    ]
    return Counter(gdpr_events)


def print_trace_summary(title, trace):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(f"Total events: {len(trace)}")

    gdpr_summary = summarize_gdpr_events(trace)
    print(f"GDPR events ({sum(gdpr_summary.values())} total):")

    for event, count in gdpr_summary.items():
        print(f"  - {event}: {count}")


@pytest.fixture
def original_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return log[0]


def test_pipeline_is_idempotent(original_trace):
    """
    Applying the GDPR pipeline twice must not change the trace.
    """

    trace_1 = build_compliant_trace(original_trace)
    trace_2 = build_compliant_trace(trace_1)

    # ---- Output for inspection ----
    print_trace_summary("TRACE AFTER FIRST PIPELINE RUN", trace_1)
    print_trace_summary("TRACE AFTER SECOND PIPELINE RUN", trace_2)

    # ---- Structural assertions ----
    assert len(trace_1) == len(trace_2), (
        "Trace length changed after second pipeline run"
    )

    assert summarize_gdpr_events(trace_1) == summarize_gdpr_events(trace_2), (
        "GDPR events differ after reapplying the pipeline"
    )

    # ---- Attribute-level idempotency ----
    assert trace_1.attributes == trace_2.attributes, (
        "Trace attributes changed after second pipeline run"
    )
