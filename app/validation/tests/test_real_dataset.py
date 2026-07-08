import copy
import os
import json
from datetime import datetime

import pm4py

from app.services.trace_builder import build_traces_from_pm4py_log
from app.services.trace_context_inferer import TraceContextInferer, GDPRContextNormalizer
from app.services.gdpr_log_enricher import GDPRLogEnricher
from app.services.pm4py_log_converter import traces_to_pm4py_log

from app.validation.ocl_engine import OCLEngine


# =====================================================
# INPUT
# =====================================================

INPUT_LOG = r"data\input\BPI Challenge 2017.xes.gz"

BASE_OUTPUT_DIR = r"data\output"

# =====================================================
# DATASET NAME
# =====================================================

dataset_filename = os.path.basename(INPUT_LOG)

dataset_name = dataset_filename

# elimina extensiones
if dataset_name.endswith(".xes.gz"):
    dataset_name = dataset_name[:-7]

elif dataset_name.endswith(".xes"):
    dataset_name = dataset_name[:-4]

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

dataset_output_dir = os.path.join(
    BASE_OUTPUT_DIR,
    f"{dataset_name}_{timestamp}"
)

os.makedirs(dataset_output_dir, exist_ok=True)

# =====================================================
# OUTPUT FILES
# =====================================================

ENRICHED_LOG_PATH = os.path.join(
    dataset_output_dir,
    f"{dataset_name}_enriched.xes"
)


REPORT_AFTER_PATH = os.path.join(
    dataset_output_dir,
    f"{dataset_name}_validation_after.json"
)

ERROR_TRACES_AFTER_PATH = os.path.join(
    dataset_output_dir,
    f"{dataset_name}_errors_after.json"
)

SUMMARY_PATH = os.path.join(
    dataset_output_dir,
    f"{dataset_name}_summary.json"
)

# =====================================================
# LOAD EVENT LOG
# =====================================================

print("=" * 80)
print("LOADING EVENT LOG")
print("=" * 80)

log = pm4py.read_xes(INPUT_LOG)

if hasattr(log, "columns"):
    log = pm4py.convert_to_event_log(log)

print(f"Traces loaded: {len(log)}")

# =====================================================
# BUILD INTERNAL TRACES
# =====================================================

print("\n" + "=" * 80)
print("BUILDING INTERNAL TRACES")
print("=" * 80)

original_traces = build_traces_from_pm4py_log(log)

print(f"Internal traces created: {len(original_traces)}")

# =====================================================
# INFER CONTEXT
# =====================================================

print("\n" + "=" * 80)
print("INFERRING DATASET CONTEXT")
print("=" * 80)

dataset_context = TraceContextInferer.infer_dataset_context(
    original_traces
)

strict_context = GDPRContextNormalizer.normalize(
    copy.deepcopy(dataset_context)
)

print(dataset_context)


# =====================================================
# ENRICHMENT
# =====================================================

print("\n" + "=" * 80)
print("ENRICHING LOG")
print("=" * 80)

enricher = GDPRLogEnricher()

enriched_traces = enricher.enrich_log(original_traces)

print(f"Enriched traces: {len(enriched_traces)}")

# =====================================================
# EXPORT ENRICHED LOG
# =====================================================

print("\n" + "=" * 80)
print("EXPORTING ENRICHED LOG")
print("=" * 80)

enriched_log = traces_to_pm4py_log(
    enriched_traces,
    context=strict_context
)

pm4py.write_xes(
    enriched_log,
    ENRICHED_LOG_PATH
)

print(ENRICHED_LOG_PATH)

# =====================================================
# VALIDATION AFTER ENRICHMENT
# =====================================================

print("\n" + "=" * 80)
print("VALIDATING ENRICHED LOG")
print("=" * 80)

engine = OCLEngine()

validation_errors = engine.validate_traces(enriched_traces)

after_results = []
after_error_traces = []

after_compliant = 0
after_non_compliant = 0
after_total_errors = 0

# -----------------------------------------------------
# BUILD RESULTS
# -----------------------------------------------------

for trace in enriched_traces:

    trace_errors = validation_errors.get(trace.trace_id, [])

    result = {
        "trace": trace.trace_id,
        "compliant": len(trace_errors) == 0,
        "errors": trace_errors
    }

    after_results.append(result)

    # -------------------------------------------------

    if trace_errors:

        after_non_compliant += 1
        after_total_errors += len(trace_errors)

        after_error_traces.append(result)

        print(f"\n❌ TRACE: {trace.trace_id}")

        for err in trace_errors:

            print(
                f"   - [{err['rule']}] "
                f"{err['event']} -> "
                f"{err['message']}"
            )

    else:

        after_compliant += 1

# =====================================================
# SUMMARY
# =====================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

summary = {

    "dataset": dataset_name,

    "before_enrichment": {

        "total_traces": len(original_traces),
    },

    "after_enrichment": {

        "total_traces": len(enriched_traces),
        "compliant_traces": after_compliant,
        "non_compliant_traces": after_non_compliant,
        "total_errors": after_total_errors
    },

    "dataset_context": str(dataset_context)
}

print(json.dumps(summary, indent=4))

# =====================================================
# EXPORT REPORTS
# =====================================================

print("\n" + "=" * 80)
print("EXPORTING REPORTS")
print("=" * 80)

with open(REPORT_AFTER_PATH, "w", encoding="utf-8") as f:
    json.dump(after_results, f, indent=4)

with open(ERROR_TRACES_AFTER_PATH, "w", encoding="utf-8") as f:
    json.dump(after_error_traces, f, indent=4)

with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print(f"Output folder:")
print(dataset_output_dir)

print("\nDONE")