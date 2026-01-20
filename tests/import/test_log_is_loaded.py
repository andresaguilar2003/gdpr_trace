from gdpr.importers import load_event_log

def test_log_is_loaded():
    log = load_event_log("data/input/log_original.xes")

    print("\n==============================")
    print("LOG LOADED")
    print("==============================")
    print(f"Number of traces: {len(log)}")

    assert len(log) > 0, "The log should contain at least one trace"

    first_trace = log[0]
    print(f"Number of events in first trace: {len(first_trace)}")

    assert len(first_trace) > 0, "The first trace should contain events"
