import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.t5.prompts.gdpr_impact_dsl_prompt import (
    GDPRImpactDSLPromptBuilder,
)
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog


DEFAULT_INPUT_DIR = Path("app/services/ai/t5/data/processed")
DEFAULT_OUTPUT_DIR = Path("app/services/ai/t5/data/processed_dsl")
SPLITS = ["train", "validation", "test"]
IMPACT_TARGETS = ["0", "1", "2"]


def load_jsonl(path):
    rows = []

    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def extract_trace_json(input_text):
    prefix = "validate gdpr enrichment:"
    text = input_text.strip()

    if text.lower().startswith(prefix):
        text = text[len(prefix):].strip()

    return json.loads(text)


def parse_target_issues(target_text, section):
    pattern = rf"{section}\s*:\s*([^|]+)"
    match = re.search(pattern, target_text, flags=re.IGNORECASE)

    if not match:
        return []

    raw_value = match.group(1).strip()

    if raw_value.lower() == "none":
        return []

    issues = []

    for raw_issue in raw_value.split(";"):
        raw_issue = raw_issue.strip()

        if not raw_issue:
            continue

        if "@" in raw_issue:
            rule, event = raw_issue.rsplit("@", 1)
        else:
            rule, event = raw_issue, "trace"

        issues.append({
            "rule": ValidationRuleCatalog.normalize_rule(rule.strip()),
            "event": event.strip(),
        })

    return issues


def target_to_rule_label(target_text):
    violations = parse_target_issues(target_text, "violations")
    warnings = parse_target_issues(target_text, "warnings")

    if violations:
        return violations[0]["rule"]

    if warnings:
        return warnings[0]["rule"]

    return "COMPLIANT"


def target_to_impact_digit(target_text):
    if parse_target_issues(target_text, "violations"):
        return "1"

    if parse_target_issues(target_text, "warnings"):
        return "2"

    return "0"


def build_dsl_record(record):
    trace_json = extract_trace_json(record["input_text"])
    rule_label = target_to_rule_label(record["target_text"])
    target = target_to_impact_digit(record["target_text"])

    return {
        "source_file": record.get("source_file", ""),
        "trace_id": record.get("trace_id", trace_json.get("traceId", "")),
        "rule_evaluated": rule_label,
        "input_text": GDPRImpactDSLPromptBuilder.build_from_trace_json(
            trace_json,
            rule_label=rule_label,
        ),
        "target_text": target,
        "impact_label": {
            "0": "0_COMPLIANT",
            "1": "1_VIOLATION",
            "2": "2_WARNING",
        }[target],
    }


def balance_by_target(rows, seed):
    grouped = {
        target: [
            row
            for row in rows
            if row["target_text"] == target
        ]
        for target in IMPACT_TARGETS
    }
    max_count = max((len(items) for items in grouped.values()), default=0)

    if max_count == 0:
        return rows

    rng = random.Random(seed)
    balanced = []

    for target in IMPACT_TARGETS:
        items = grouped[target]

        if not items:
            continue

        rng.shuffle(items)

        for index in range(max_count):
            source = dict(items[index % len(items)])
            source["sampling_strategy"] = "impact_balanced"
            source["synthetic_id"] = f"{target}_{index}"
            balanced.append(source)

    rng.shuffle(balanced)
    return balanced


def summarize(splits):
    all_rows = [
        row
        for rows in splits.values()
        for row in rows
    ]

    return {
        "total": len(all_rows),
        "splits": {
            name: len(rows)
            for name, rows in splits.items()
        },
        "impact_distribution": {
            target: sum(1 for row in all_rows if row["target_text"] == target)
            for target in IMPACT_TARGETS
        },
        "rule_count": len({
            row["rule_evaluated"]
            for row in all_rows
        }),
        "rules": sorted({
            row["rule_evaluated"]
            for row in all_rows
        }),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build balanced T5 DSL datasets with 0/1/2 impact targets."
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--no-balance",
        action="store_true",
        help="Keep the natural distribution instead of balancing each split.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    splits = {}

    for split_name in SPLITS:
        source_path = input_dir / f"{split_name}.jsonl"

        if not source_path.exists():
            raise FileNotFoundError(f"Missing source split: {source_path}")

        rows = [
            build_dsl_record(record)
            for record in load_jsonl(source_path)
        ]

        if not args.no_balance:
            rows = balance_by_target(rows, seed=args.seed)

        splits[split_name] = rows
        write_jsonl(output_dir / f"{split_name}.jsonl", rows)

    summary = summarize(splits)
    summary["source_dir"] = str(input_dir)
    summary["balanced"] = not args.no_balance
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )

    print(f"DSL dataset written to {output_dir}")
    print(json.dumps(summary, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
