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


def extract_events(trace, name):
    return [e for e in trace if e["concept:name"] == name]


def test_rights_flows_are_well_formed(compliant_trace):
    """
    Comprueba que los flujos de ejercicio de derechos GDPR
    (rectificación, restricción y borrado) están bien formados
    y respetan la semántica temporal GDPR.
    """

    print_section("ANALYSING GDPR RIGHTS FLOWS")

    rectifications = extract_events(compliant_trace, "gdpr:rectifyData")
    restrictions = extract_events(compliant_trace, "gdpr:restrictProcessing")
    lifts = extract_events(compliant_trace, "gdpr:liftProcessingRestriction")
    erasures = extract_events(compliant_trace, "gdpr:eraseData")

    # ---- Output informativo ----
    print(f"Rectification events: {len(rectifications)}")
    for e in rectifications:
        print(f"  RECTIFY  | {e['time:timestamp']}")

    print(f"\nProcessing restrictions: {len(restrictions)}")
    for e in restrictions:
        print(f"  RESTRICT | {e['time:timestamp']}")

    print(f"\nRestriction lifts: {len(lifts)}")
    for e in lifts:
        print(f"  LIFT     | {e['time:timestamp']}")

    print(f"\nErase requests: {len(erasures)}")
    for e in erasures:
        print(f"  ERASE    | {e['time:timestamp']}")

    # ---- Assertions ----

    # 1. Rectification should be unique
    assert len(rectifications) <= 1, (
        "Multiple rectification events detected in compliant trace"
    )

    # 2. Restriction semantics
    if restrictions:
        restriction_ts = restrictions[0]["time:timestamp"]

        if erasures:
            erase_ts = erasures[0]["time:timestamp"]

            # If data is erased before restriction ends, lift is not required
            if erase_ts > restriction_ts:
                assert len(lifts) == 0 or lifts[0]["time:timestamp"] < erase_ts, (
                    "Restriction lift should not occur after data erasure"
                )
        else:
            # No erasure → restriction must be lifted
            assert len(lifts) == 1, (
                "Processing restriction was not properly lifted"
            )
            assert lifts[0]["time:timestamp"] > restriction_ts, (
                "Restriction lift occurs before restriction"
            )

    # 3. Erasure should be unique
    assert len(erasures) <= 1, (
        "Multiple eraseData events detected in compliant trace"
    )
