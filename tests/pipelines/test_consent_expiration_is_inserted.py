# tests/pipelines/test_consent_expiration_is_inserted.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS
from datetime import timedelta


def test_consent_expiration_is_inserted():
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    send_event = None
    consent_event = None
    expiration_event = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["SEND_DATA"]:
            send_event = e
        elif e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = e
        elif e["concept:name"] == GDPR_EVENTS["CONSENT_EXPIRED"]:
            expiration_event = e

    assert send_event is not None, "sendData event not found"
    assert consent_event is not None, "giveConsent event not found"
    assert expiration_event is not None, "consentExpired event not found"

    max_time_days = send_event.get("gdpr:maxTime")
    assert max_time_days is not None, "gdpr:maxTime not found in sendData"

    expected_expiration = consent_event["time:timestamp"] + timedelta(days=max_time_days)
    actual_expiration = expiration_event["time:timestamp"]

    print("\n==============================")
    print("CONSENT EXPIRATION CHECK")
    print("==============================")
    print(f"Consent given at:     {consent_event['time:timestamp']}")
    print(f"Max time (days):      {max_time_days}")
    print(f"Expected expiration: {expected_expiration}")
    print(f"Actual expiration:   {actual_expiration}")

    assert actual_expiration == expected_expiration, (
        "consentExpired timestamp does not match consent + maxTime"
    )
