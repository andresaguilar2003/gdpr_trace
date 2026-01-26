# tests/compliant/test_gdpr_invariants.py

import pytest

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace


@pytest.fixture
def compliant_trace():
    log = load_event_log("data/input/Sepsis Cases - Event Log.xes.gz")
    return build_compliant_trace(log[0])


def is_personal_data_access(event):
    return event.get("gdpr:access") is True


def test_no_access_without_consent(compliant_trace):
    """
    Invariant:
    No access to personal data may occur before explicit consent.
    """

    consent_given = False

    for event in compliant_trace:
        if event["concept:name"] == "gdpr:giveConsent":
            consent_given = True

        if is_personal_data_access(event):
            assert consent_given, (
                f"Personal data access before consent at "
                f"{event['time:timestamp']} ({event['concept:name']})"
            )


def test_no_access_after_erase(compliant_trace):
    """
    Invariant:
    After eraseData, no further access to personal data is allowed.
    """

    erased = False

    for event in compliant_trace:
        if event["concept:name"] == "gdpr:eraseData":
            erased = True

        if erased and is_personal_data_access(event):
            pytest.fail(
                f"Access after eraseData at "
                f"{event['time:timestamp']} ({event['concept:name']})"
            )


def test_no_access_during_processing_restriction(compliant_trace):
    """
    Invariant:
    No access is allowed while processing restriction is active.
    """

    restriction_active = False

    for event in compliant_trace:
        if event["concept:name"] == "gdpr:restrictProcessing":
            restriction_active = True

        if event["concept:name"] == "gdpr:liftProcessingRestriction":
            restriction_active = False

        if restriction_active and is_personal_data_access(event):
            pytest.fail(
                f"Access during processing restriction at "
                f"{event['time:timestamp']} ({event['concept:name']})"
            )
