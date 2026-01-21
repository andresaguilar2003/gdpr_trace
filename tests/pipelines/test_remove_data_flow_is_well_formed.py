# tests/pipelines/test_remove_data_flow_is_well_formed.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS


def test_remove_data_flow_is_well_formed():
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    remove_event = None
    search_event = None
    erase_event = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["REMOVE_REQUEST"]:
            remove_event = e
        elif e["concept:name"] == GDPR_EVENTS["SEARCH_LOCATION"]:
            search_event = e
        elif e["concept:name"] == GDPR_EVENTS["ERASE"]:
            erase_event = e

    print("\n==============================")
    print("REMOVE DATA FLOW CHECK")
    print("==============================")

    # El flujo es opcional → si no existe, el test no falla
    if remove_event is None:
        print("No removeData flow present in this trace (allowed).")
        return

    assert search_event is not None, "searchDataLocation missing after removeData"
    assert erase_event is not None, "eraseData missing after removeData"

    print(f"removeData at:        {remove_event['time:timestamp']}")
    print(f"searchDataLocation:  {search_event['time:timestamp']}")
    print(f"eraseData at:        {erase_event['time:timestamp']}")

    # Orden temporal correcto
    assert (
        remove_event["time:timestamp"]
        <= search_event["time:timestamp"]
        <= erase_event["time:timestamp"]
    ), "Remove data flow events are not in correct order"

    # Restricción temporal legal
    deadline = erase_event.get("gdpr:deadline")
    assert deadline is not None, "eraseData has no gdpr:deadline"

    print(f"eraseData deadline:  {deadline}")

    assert (
        erase_event["time:timestamp"] <= deadline
    ), "eraseData executed after legal deadline"
