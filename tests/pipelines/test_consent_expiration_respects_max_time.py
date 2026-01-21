# tests/pipelines/test_consent_expiration_respects_max_time.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS
from datetime import timedelta


def test_consent_expiration_respects_max_time():
    """
    Verifica que, si se inserta un evento gdpr:consentExpired,
    este ocurre después de que se supere el gdpr:maxTime definido
    en el evento gdpr:sendData (Figura 3 – loop temporal).
    """

    log = load_event_log("data/input/test/log_long_case.xes")
    raw_trace = log[0]
    gdpr_trace = build_compliant_trace(raw_trace)

    print("\n==============================")
    print("CONSENT EXPIRATION TIME CHECK")
    print("==============================")

    send_data = None
    consent = None
    consent_expired = None

    for e in gdpr_trace:
        if e["concept:name"] == GDPR_EVENTS["SEND_DATA"]:
            send_data = e
        elif e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent = e
        elif e["concept:name"] == GDPR_EVENTS["CONSENT_EXPIRED"]:
            consent_expired = e

    if not consent_expired:
        print("No consentExpired event present in this trace (allowed by the model).")
        return

    assert send_data is not None, "sendData must exist if consentExpired exists"
    assert consent is not None, "giveConsent must exist if consentExpired exists"

    max_time_days = send_data.get("gdpr:maxTime")
    assert max_time_days is not None, "sendData must define gdpr:maxTime"

    expected_min_expiration = consent["time:timestamp"] + timedelta(days=max_time_days)

    print(f"Consent given at:      {consent['time:timestamp']}")
    print(f"Max allowed time:      {max_time_days} days")
    print(f"Expected expiration ≥ {expected_min_expiration}")
    print(f"Actual expiration:    {consent_expired['time:timestamp']}")

    assert consent_expired["time:timestamp"] >= expected_min_expiration, (
        "consentExpired occurred before maxTime was exceeded"
    )
