from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace

def test_gdpr_context_is_added():
    log = load_event_log("data/input/log_original.xes")
    raw_trace = log[0]

    gdpr_trace = build_compliant_trace(raw_trace)

    print("\n==============================")
    print("TRACE ATTRIBUTES (AFTER GDPR ENRICHMENT)")
    print("==============================")

    for k, v in gdpr_trace.attributes.items():
        print(f"{k}: {v}")

    assert "gdpr:personal_data" in gdpr_trace.attributes
    assert "gdpr:legal_basis" in gdpr_trace.attributes
    assert "gdpr:default_purpose" in gdpr_trace.attributes
