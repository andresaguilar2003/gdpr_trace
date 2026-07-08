import argparse
import json
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import pm4py

from app.services.ai.t5.training.dataset_generator import DatasetGenerator
from app.services.trace_builder import build_traces_from_pm4py_log
from app.validation.ocl_engine import OCLEngine


DEFAULT_INPUT_DIR = Path("app/validation/data")
DEFAULT_OUTPUT_DIR = Path("app/services/ai/t5/data/processed")


def extract_log_context_from_xes(path):
    tree = ET.parse(path)
    root = tree.getroot()
    namespace = {"xes": "http://www.xes-standard.org/"}
    context = {}

    for item in root.findall("xes:string", namespace):
        context[item.get("key")] = item.get("value")

    return context


def apply_context(traces, raw_context):
    for trace in traces:
        trace.context.legal_basis = raw_context.get("gdpr:legal_basis")
        trace.context.data_category = raw_context.get("gdpr:data_category")
        trace.context.retention_period = raw_context.get("gdpr:retention_period")
        trace.context.has_third_party_recipients = (
            raw_context.get("gdpr:has_third_party_recipients") == "true"
        )
        trace.context.international_transfer = raw_context.get(
            "gdpr:international_transfer"
        )
        trace.context.transfer_safeguard = raw_context.get(
            "gdpr:transfer_safeguard"
        )


def load_traces(path):
    log = pm4py.read_xes(str(path))

    if hasattr(log, "columns"):
        log = pm4py.convert_to_event_log(log)

    traces = build_traces_from_pm4py_log(log)
    apply_context(traces, extract_log_context_from_xes(path))

    return traces


def build_records(input_dir):
    engine = OCLEngine()
    records = []

    for path in sorted(input_dir.rglob("*.xes")):
        traces = load_traces(path)

        for trace in traces:
            result = engine.validate_trace(trace)
            example = DatasetGenerator.build_example(trace, result)

            records.append({
                "source_file": str(path),
                "trace_id": trace.trace_id,
                "input_text": example.input_text,
                "target_text": example.target_text,
                "is_valid": len(result.get("violations", [])) == 0,
                "violation_count": len(result.get("violations", [])),
                "warning_count": len(result.get("warnings", []))
            })

    return records


def split_records(records, validation_ratio, test_ratio, seed):
    shuffled = list(records)
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)
    test_count = int(total * test_ratio)
    validation_count = int(total * validation_ratio)

    test = shuffled[:test_count]
    validation = shuffled[test_count:test_count + validation_count]
    train = shuffled[test_count + validation_count:]

    return {
        "train": train,
        "validation": validation,
        "test": test
    }


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=True) + "\n")


def write_summary(path, splits):
    all_records = [
        record
        for records in splits.values()
        for record in records
    ]

    summary = {
        "total": len(all_records),
        "valid": sum(1 for record in all_records if record["is_valid"]),
        "invalid": sum(1 for record in all_records if not record["is_valid"]),
        "splits": {
            name: len(records)
            for name, records in splits.items()
        }
    }

    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True),
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build T5 JSONL datasets from GDPR validation XES files."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--validation-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    records = build_records(input_dir)
    splits = split_records(
        records,
        validation_ratio=args.validation_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed
    )

    for split_name, split_records_ in splits.items():
        write_jsonl(output_dir / f"{split_name}.jsonl", split_records_)

    write_summary(output_dir / "summary.json", splits)

    print(f"Dataset written to {output_dir}")
    print(f"Total examples: {len(records)}")


if __name__ == "__main__":
    main()
