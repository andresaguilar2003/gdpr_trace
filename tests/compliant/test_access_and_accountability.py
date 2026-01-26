# tests/compliant/test_access_and_accountability.py

import pytest

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


@pytest.fixture
def compliant_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return build_compliant_trace(log[0])


def test_access_and_accountability_flow(compliant_trace):
    """
    Comprueba que los accesos a datos personales quedan correctamente
    reflejados mediante accessLog y updateAccessHistory.
    """

    print_section("ANALYSING ACCESS AND ACCOUNTABILITY")

    access_logs = []
    update_events = []

    for e in compliant_trace:
        if e["concept:name"] == "gdpr:accessLog":
            access_logs.append(e)

        if e["concept:name"] == "gdpr:updateAccessHistory":
            update_events.append(e)

    # ---- Output informativo ----
    print(f"Access logs generated: {len(access_logs)}")
    for e in access_logs[:5]:  # no saturar
        print(
            f"  LOG | {e['time:timestamp']} | "
            f"purpose={e.get('gdpr:purpose')} | actor={e.get('gdpr:actor')}"
        )

    if len(access_logs) > 5:
        print(f"  ... ({len(access_logs) - 5} more accessLog events)")

    print(f"\nAccess history updates: {len(update_events)}")

    # ---- Assertions ----

    # 1. There must be access logs if personal data is processed
    assert len(access_logs) > 0, (
        "No accessLog events generated despite personal data processing"
    )

    # 2. Exactly one updateAccessHistory must summarize the accesses
    assert len(update_events) == 1, (
        "Expected exactly one updateAccessHistory event"
    )
