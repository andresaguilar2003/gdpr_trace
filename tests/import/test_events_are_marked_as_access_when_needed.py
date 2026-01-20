from gdpr.importers import load_event_log

def test_events_are_marked_as_access_when_needed():
    log = load_event_log("data/input/log_original.xes")
    trace = log[0]

    print("\n==============================")
    print("EVENT ACCESS INSPECTION")
    print("==============================")

    access_events = []

    for i, e in enumerate(trace):
        access = e.get("gdpr:access")
        print(
            f"{i:02d} | {e['concept:name']} | gdpr:access={access}"
        )

        if access is not None:
            access_events.append(e)

    assert len(access_events) > 0, "There should be at least one access to personal data"
