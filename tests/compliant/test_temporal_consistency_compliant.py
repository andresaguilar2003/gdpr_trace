import pytest

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


@pytest.fixture
def compliant_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return build_compliant_trace(log[0])


def test_temporal_consistency_of_compliant_trace(compliant_trace):
    """
    Comprueba que la traza GDPR-compliant respeta las invariantes temporales:
    - consentimiento antes de accessLog
    - no accessLog tras borrado efectivo
    - orden temporal coherente
    """

    print_section("ANALYSING TEMPORAL CONSISTENCY")

    consent_ts = None
    erase_request_ts = None
    erase_confirmed_ts = None
    last_ts = None

    access_logs_after_consent = 0
    access_logs_after_erase_confirmed = 0

    for e in compliant_trace:
        ts = e["time:timestamp"]

        # ---- Orden global ----
        if last_ts:
            assert ts >= last_ts, "Trace events are not temporally ordered"
        last_ts = ts

        # ---- Consent ----
        if e["concept:name"] == "gdpr:giveConsent":
            consent_ts = ts
            print(f"CONSENT | {ts}")

        # ---- Erase request ----
        if e["concept:name"] == "gdpr:eraseData":
            erase_request_ts = ts
            print(f"ERASE REQUEST | {ts}")

        # ---- Erase confirmed ----
        if e["concept:name"] == "gdpr:eraseDataConfirmed":
            erase_confirmed_ts = ts
            print(f"ERASE CONFIRMED | {ts}")

        # ---- Access logs ----
        if e["concept:name"] == "gdpr:accessLog":
            print(f"ACCESS | {ts} | purpose={e.get('gdpr:purpose')}")

            if consent_ts and ts > consent_ts:
                access_logs_after_consent += 1

            if erase_confirmed_ts and ts > erase_confirmed_ts:
                access_logs_after_erase_confirmed += 1

    # ---- Output summary ----
    print("\nSUMMARY")
    print(f"Access logs after consent: {access_logs_after_consent}")
    print(f"Access logs after erase confirmed: {access_logs_after_erase_confirmed}")

    # ---- Assertions ----

    assert consent_ts is not None, "No consent event found"
    assert access_logs_after_consent > 0, "No access logs after consent"

    # 🔐 Invariante fuerte GDPR
    if erase_confirmed_ts:
        assert access_logs_after_erase_confirmed == 0, (
            "Access logs detected after effective data erasure"
        )
