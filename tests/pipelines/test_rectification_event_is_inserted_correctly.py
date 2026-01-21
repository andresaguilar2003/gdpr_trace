# tests/pipelines/test_rectification_event_is_inserted_correctly.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS


def test_rectification_event_is_inserted_correctly():
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    consent_event = None
    rectify_event = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = e
        elif e["concept:name"] == GDPR_EVENTS["RECTIFY"]:
            rectify_event = e

    print("\n==============================")
    print("RECTIFICATION FLOW CHECK")
    print("==============================")

    # El flujo es opcional
    if rectify_event is None:
        print("No rectification event present in this trace (allowed).")
        return

    assert consent_event is not None, "Rectification without prior consent"

    print(f"Consent at:     {consent_event['time:timestamp']}")
    print(f"Rectify at:     {rectify_event['time:timestamp']}")

    # Orden temporal correcto
    assert (
        rectify_event["time:timestamp"] > consent_event["time:timestamp"]
    ), "Rectification occurs before consent"

    # Propiedades GDPR correctas
    assert rectify_event.get("gdpr:event") is True
    assert rectify_event.get("gdpr:actor") == "Controller"
    assert rectify_event.get("gdpr:purpose") == "data_rectification"
