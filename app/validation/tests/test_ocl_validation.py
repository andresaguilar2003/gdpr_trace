from collections import defaultdict

import pm4py

from app.services.trace_builder import build_traces_from_pm4py_log
from app.services.gdpr_log_enricher import GDPRLogEnricher
from app.validation.ocl_engine import OCLEngine


import xml.etree.ElementTree as ET


#LOG_PATH = "app/validation/data/case_start/case_start_valid.xes"
LOG_PATH = "app/validation/data/case_start/case_start_invalid.xes"

#LOG_PATH = "app/validation/data/data_collection/valid_consent.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_no_consent_allowed.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_missing_consent.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_missing_notice.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_notice_wrong_position.xes"
#LOG_PATH = "app/validation/data/data_processing/valid_log_processing_after.xes"
#LOG_PATH = "app/validation/data/data_processing/invalid_missing_log_processing.xes"


#LOG_PATH = "app/validation/data/data_access/data_access_health.xes"
#LOG_PATH = "app/validation/data/data_access/data_access_invalid_standard.xes"
#LOG_PATH = "app/validation/data/data_access/data_access_invalid.xes"


#LOG_PATH = "app/validation/data/data_collection/valid_legal_basis_flow.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_missing_case_start.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_missing_verify_legal_basis.xes"
#LOG_PATH = "app/validation/data/data_collection/invalid_missing_record_purpose.xes"
#LOG_PATH = "app/validation/data/data_processing/invalid_missing_encryption.xes"
#LOG_PATH = "app/validation/data/data_processing/invalid_standard_with_encryption.xes"
#LOG_PATH = "app/validation/data/data_processing/valid_standard_no_encryption.xes"
#LOG_PATH = "app/validation/data/data_processing/invalid_missing_minimisation.xes"

#LOG_PATH = "app/validation/data/data_transfer/valid.xes"
#LOG_PATH = "app/validation/data/data_transfer/invalid_third_party_check.xes"
#LOG_PATH = "app/validation/data/data_transfer/invalid_missing_safeguard.xes"
#LOG_PATH = "app/validation/data/data_transfer/invalid_forbidden_third_party.xes"
#LOG_PATH = "app/validation/data/data_transfer/invalid_forbidden_safeguard.xes"


#LOG_PATH = "app/validation/data/automated_decision/invalid_missing_disclosure.xes"
#LOG_PATH = "app/validation/data/automated_decision/valid_automated_decision.xes"

#LOG_PATH = "app/validation/data/user_rights/valid_user_right_request.xes"
#LOG_PATH = "app/validation/data/user_rights/invalid_user_right_request_missing_response.xes"


#LOG_PATH = "app/validation/data/data_deletion/valid_data_deletion.xes"
#LOG_PATH = "app/validation/data/data_deletion/invalid_data_deletion_missing_erase.xes"
#LOG_PATH = "app/validation/data/data_deletion/invalid_data_deletion_missing_retention.xes"

#LOG_PATH = "app/validation/data/case_end/case_end_valid.xes"
#LOG_PATH = "app/validation/data/case_end/case_end_erasure.xes"
#LOG_PATH = "app/validation/data/case_end/case_end_retention.xes"

#LOG_PATH = "app/validation/data/position/wrong_position.xes"

def extract_log_context_from_xes(path):

    tree = ET.parse(path)
    root = tree.getroot()

    ns = {"xes": "http://www.xes-standard.org/"}

    context = {}

    for string in root.findall("xes:string", ns):

        key = string.get("key")
        value = string.get("value")

        context[key] = value

    return context


# =====================================================
# LOAD + VALIDATE
# =====================================================

def run():

    print("\n" + "=" * 70)
    print("📄 GDPR VALIDATION TEST")
    print("=" * 70)

    # -------------------------------------------------
    # LOAD LOG
    # -------------------------------------------------

    print("\n=== LOADING LOG ===")

    log = pm4py.read_xes(LOG_PATH)

    # PM4PY dataframe protection
    if hasattr(log, "columns"):
        log = pm4py.convert_to_event_log(log)

    raw_ctx = extract_log_context_from_xes(LOG_PATH)

    traces = build_traces_from_pm4py_log(log)

    # -------------------------------------------------
    # INJECT CONTEXT
    # -------------------------------------------------

    for t in traces:

        t.context.legal_basis = raw_ctx.get("gdpr:legal_basis")

        t.context.data_category = raw_ctx.get(
            "gdpr:data_category"
        )

        t.context.retention_period = raw_ctx.get(
            "gdpr:retention_period"
        )

        t.context.has_third_party_recipients = (
            raw_ctx.get("gdpr:has_third_party_recipients")
            == "true"
        )

        t.context.international_transfer = raw_ctx.get(
            "gdpr:international_transfer"
        )

    print(f"\n✅ Traces loaded: {len(traces)}")

    # -------------------------------------------------
    # PRINT CONTEXT
    # -------------------------------------------------

    print("\n📌 CONTEXT")

    print(f"   legal_basis: {raw_ctx.get('gdpr:legal_basis')}")
    print(f"   data_category: {raw_ctx.get('gdpr:data_category')}")
    print(f"   retention_period: {raw_ctx.get('gdpr:retention_period')}")
    print(
        f"   third_party: "
        f"{raw_ctx.get('gdpr:has_third_party_recipients')}"
    )
    print(
        f"   international_transfer: "
        f"{raw_ctx.get('gdpr:international_transfer')}"
    )

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------

    print("\n=== VALIDATING ===")

    engine = OCLEngine()

    results = engine.validate_traces(traces)

    # =====================================================
    # GLOBAL RESULT
    # =====================================================

    if not results:

        print("\n✅ RESULT: PASS")
        return

    has_any_violation = any(
        len(res.get("violations", [])) > 0
        for res in results.values()
    )

    if has_any_violation:
        print("\n❌ RESULT: FAIL (Strict GDPR Violations Found)")
    else:
        print("\n⚠️ RESULT: PASS (With Warnings)")

    # =====================================================
    # DETAILED OUTPUT
    # =====================================================

    total_violations = 0
    total_warnings = 0

    for trace_id, result in results.items():

        violations = result.get("violations", [])
        warnings = result.get("warnings", [])

        if not violations and not warnings:
            continue

        print("\n" + "-" * 60)
        print(f"🔎 TRACE: {trace_id}")
        print("-" * 60)

        # -------------------------------------------------
        # VIOLATIONS
        # -------------------------------------------------

        if violations:

            grouped_viols = defaultdict(list)

            for v in violations:
                grouped_viols[v["rule"]].append(v)

            print("\n🔴 CRITICAL VIOLATIONS")

            for rule, items in grouped_viols.items():

                print(
                    f"\n🚫 Rule: {rule} "
                    f"({len(items)} violation(s))"
                )

                for v in items:

                    event = v.get("event", "")
                    msg = v.get("message", "")

                    print(f"   → [{event}] {msg}")

            total_violations += len(violations)

        # -------------------------------------------------
        # WARNINGS
        # -------------------------------------------------

        if warnings:

            grouped_warns = defaultdict(list)

            for w in warnings:
                grouped_warns[w["rule"]].append(w)

            print("\n🟡 NON-CRITICAL WARNINGS")

            for rule, items in grouped_warns.items():

                print(
                    f"\n⚠️ Rule: {rule} "
                    f"({len(items)} warning(s))"
                )

                for w in items:

                    event = w.get("event", "")
                    msg = w.get("message", "")

                    print(f"   → [{event}] {msg}")

            total_warnings += len(warnings)

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    print(f"Violations: {total_violations}")
    print(f"Warnings:   {total_warnings}")

    print("=" * 70)


if __name__ == "__main__":
    run()