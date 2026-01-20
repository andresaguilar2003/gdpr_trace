from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace

def test_access_events_are_inferred():
    log = load_event_log("data/input/log_original.xes")
    raw_trace = log[0]

    gdpr_trace = build_compliant_trace(raw_trace)

    print("\n==============================")
    print("ACCESS EVENTS AFTER ENRICHMENT")
    print("==============================")

    access_events = []

    for i, e in enumerate(gdpr_trace):
        access = e.get("gdpr:access")
        print(
            f"{i:02d} | {e['concept:name']} | gdpr:access={access}"
        )

        if access:
            access_events.append(e)

    assert len(access_events) > 0
    