from gdpr.importers import load_event_log

def test_events_have_no_access_flag_initially():
    log = load_event_log("data/input/log_original.xes")
    trace = log[0]

    print("\n==============================")
    print("RAW EVENTS (NO GDPR ACCESS)")
    print("==============================")

    for i, e in enumerate(trace):
        print(
            f"{i:02d} | {e['concept:name']} | gdpr:access={e.get('gdpr:access')}"
        )
        assert "gdpr:access" not in e
