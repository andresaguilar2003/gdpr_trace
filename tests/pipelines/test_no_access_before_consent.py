# tests/pipelines/test_no_access_before_consent.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS


def test_no_access_before_consent():
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    # Localizar el consentimiento
    consent_event = None
    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = e
            break

    assert consent_event is not None, "Consent event (giveConsent) not found in trace"

    consent_ts = consent_event["time:timestamp"]

    print("\n==============================")
    print("CONSENT EVENT")
    print("==============================")
    print(f"Consent at: {consent_ts}")

    print("\n==============================")
    print("ACCESS EVENTS CHECK")
    print("==============================")

    violations = []

    for i, e in enumerate(trace):
        if e.get("gdpr:access"):
            access_ts = e["time:timestamp"]
            print(
                f"{i:02d} | {e['concept:name']} | access={e['gdpr:access']} | time={access_ts}"
            )

            if access_ts < consent_ts:
                violations.append(e)

    assert not violations, (
        "There are access events occurring before consent was given"
    )
