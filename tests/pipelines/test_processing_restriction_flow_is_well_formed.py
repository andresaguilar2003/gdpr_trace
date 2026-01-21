# tests/pipelines/test_processing_restriction_flow_is_well_formed.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS


def test_processing_restriction_flow_is_well_formed():
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    consent = None
    restrict = None
    lift = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent = e
        elif e["concept:name"] == GDPR_EVENTS["RESTRICT"]:
            restrict = e
        elif e["concept:name"] == GDPR_EVENTS["LIFT_RESTRICTION"]:
            lift = e

    print("\n==============================")
    print("PROCESSING RESTRICTION FLOW")
    print("==============================")

    # Flujo opcional
    if restrict is None:
        print("No processing restriction present in this trace (allowed).")
        return

    assert consent is not None, "Restriction without prior consent"
    assert lift is not None, "Restriction without liftRestriction event"

    print(f"Consent at:          {consent['time:timestamp']}")
    print(f"Restriction at:      {restrict['time:timestamp']}")
    print(f"Lift restriction at: {lift['time:timestamp']}")

    # Orden temporal correcto
    assert (
        consent["time:timestamp"] < restrict["time:timestamp"]
    ), "Restriction occurs before consent"

    assert (
        restrict["time:timestamp"] < lift["time:timestamp"]
    ), "Restriction is lifted before it is applied"

    # Propiedades GDPR
    for ev in (restrict, lift):
        assert ev.get("gdpr:event") is True
        assert ev.get("gdpr:actor") in {"User", "Controller"}
        assert ev.get("gdpr:purpose") is not None
