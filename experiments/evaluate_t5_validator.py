import argparse
import csv
import json
import re
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.t5.t5_client import T5Client
from app.services.ai.t5.prompts.gdpr_impact_dsl_prompt import (
    GDPRImpactDSLPromptBuilder,
)
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog
from app.services.ai.t5.validators.impact_parser import parse_impact_response
from app.mutations.registry.mutation_registry import MUTATION_REGISTRY


DATA_DIR = ROOT / "app" / "services" / "ai" / "t5" / "data" / "processed"
DEFAULT_MODEL_PATH = ROOT / "app" / "services" / "ai" / "t5" / "models" / "gdpr_t5_validator"
DEFAULT_DSL_MODEL_PATH = ROOT / "app" / "services" / "ai" / "t5" / "models" / "gdpr_t5_impact_dsl"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "results_t5"
IMPACT_LABELS = ["0_COMPLIANT", "1_VIOLATION", "2_WARNING"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark T5 JSON baseline vs simplified DSL + 0/1/2 impact validation."
    )
    parser.add_argument(
        "--data-dir",
        default=str(DATA_DIR),
        help="Directory containing train/validation/test jsonl files.",
    )
    parser.add_argument(
        "--split",
        default="all",
        choices=["train", "validation", "test", "all"],
        help="Dataset split to evaluate.",
    )
    parser.add_argument(
        "--baseline-model",
        default=str(DEFAULT_MODEL_PATH),
        help="T5 model path for the current JSON baseline.",
    )
    parser.add_argument(
        "--simplified-model",
        default=str(DEFAULT_DSL_MODEL_PATH) if DEFAULT_DSL_MODEL_PATH.exists() else None,
        help=(
            "Optional T5 model path for the DSL approach. "
            "If omitted, the baseline model is reused. If present, "
            "app/services/ai/t5/models/gdpr_t5_impact_dsl is used by default."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where benchmark artifacts will be written.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=0,
        help="Limit evaluated examples. Use 0 for all selected examples.",
    )
    parser.add_argument(
        "--no-balance-impact",
        action="store_true",
        help="Disable impact-class balancing. By default the evaluation is balanced over 0/1/2.",
    )
    return parser.parse_args()


def load_jsonl(path):
    rows = []

    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def load_examples(data_dir, split):
    data_dir = Path(data_dir)
    splits = ["train", "validation", "test"] if split == "all" else [split]
    examples = []

    for split_name in splits:
        path = data_dir / f"{split_name}.jsonl"

        if not path.exists():
            raise FileNotFoundError(f"Missing split file: {path}")

        for row in load_jsonl(path):
            row["split"] = split_name
            examples.append(row)

    return examples


def extract_trace_json(input_text):
    prefix = "validate gdpr enrichment:"
    text = input_text.strip()

    if text.lower().startswith(prefix):
        text = text[len(prefix):].strip()

    return json.loads(text)


def normalize_rule(rule):
    return ValidationRuleCatalog.normalize_rule(rule)


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
            "rule": normalize_rule(rule.strip()),
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


def target_to_impact(target_text):
    if parse_target_issues(target_text, "violations"):
        return "1_VIOLATION"

    if parse_target_issues(target_text, "warnings"):
        return "2_WARNING"

    return "0_COMPLIANT"


def parse_baseline_prediction(response):
    violations = parse_target_issues(response, "violations")
    warnings = parse_target_issues(response, "warnings")
    lower_response = response.strip().lower()

    if violations:
        return violations[0]["rule"]

    if warnings:
        return warnings[0]["rule"]

    if lower_response.startswith("valid"):
        return "COMPLIANT"

    if lower_response.startswith("invalid"):
        return "UNKNOWN_VIOLATION"

    rule_match = re.search(r"\b[A-Z][A-Z0-9_]{3,}\b", response)

    if rule_match:
        return normalize_rule(rule_match.group(0))

    return "PARSE_ERROR"


def parse_baseline_impact_prediction(response):
    lower_response = response.strip().lower()

    if parse_target_issues(response, "violations"):
        return "1_VIOLATION"

    if parse_target_issues(response, "warnings"):
        return "2_WARNING"

    if lower_response.startswith("valid"):
        return "0_COMPLIANT"

    if lower_response.startswith("invalid"):
        return "1_VIOLATION"

    return "PARSE_ERROR"


def parse_simplified_prediction(response):
    return parse_impact_response(response)


def compact_value(value):
    if value is None:
        return "none"

    if isinstance(value, bool):
        return str(value).lower()

    return str(value).replace(" ", "_")


def simplify_rule_name(rule_label):
    rule = normalize_rule(rule_label)

    if rule == "COMPLIANT":
        return "COMPLIANCE_CHECK"

    families = [
        "CASE_START",
        "CASE_END",
        "DATA_COLLECTION",
        "DATA_PROCESSING",
        "DATA_ACCESS",
        "DATA_TRANSFER",
        "AUTOMATED_DECISION",
        "USER_RIGHT",
        "DATA_DELETION",
    ]

    for family in families:
        if rule.startswith(family):
            return family

    return rule


def build_dsl_input(trace_json, rule_label):
    return GDPRImpactDSLPromptBuilder.build_from_trace_json(
        trace_json,
        rule_label=rule_label,
    )


def build_dataset_rows(examples):
    rows = []

    for index, example in enumerate(examples):
        trace_json = extract_trace_json(example["input_text"])
        rule_label = target_to_rule_label(example["target_text"])
        impact_label = target_to_impact(example["target_text"])

        rows.append({
            "example_id": f"{example.get('split', 'split')}_{index}",
            "split": example.get("split", ""),
            "source_file": example.get("source_file", ""),
            "trace_id": example.get("trace_id", trace_json.get("traceId", "")),
            "rule_evaluated": rule_label,
            "baseline_input": example["input_text"],
            "baseline_target": example["target_text"],
            "baseline_y_true": rule_label,
            "simplified_input": build_dsl_input(trace_json, rule_label),
            "simplified_y_true": impact_label,
        })

    return rows


def balance_rows_by_impact(rows):
    grouped = {
        label: [
            row
            for row in rows
            if row["simplified_y_true"] == label
        ]
        for label in IMPACT_LABELS
    }
    max_count = max((len(items) for items in grouped.values()), default=0)

    if max_count == 0:
        return rows

    balanced = []

    for label in IMPACT_LABELS:
        items = grouped[label]

        if not items:
            continue

        for index in range(max_count):
            source = dict(items[index % len(items)])
            source["example_id"] = f"{source['example_id']}_balanced_{index}"
            source["sampling_strategy"] = "impact_balanced"
            balanced.append(source)

    return balanced


def count_impacts(rows):
    return {
        label: sum(1 for row in rows if row["simplified_y_true"] == label)
        for label in IMPACT_LABELS
    }


def build_coverage_summary(dataset_rows, source_rows=None, sampling_strategy="natural"):
    source_rows = source_rows or dataset_rows
    covered_rules = sorted({
        row["rule_evaluated"]
        for row in dataset_rows
        if row["rule_evaluated"] != "COMPLIANT"
    })
    catalog_rules = sorted(ValidationRuleCatalog.DEFAULT_MESSAGES.keys())
    covered_catalog_rules = sorted(set(catalog_rules) & set(covered_rules))
    extra_observed_rules = sorted(set(covered_rules) - set(catalog_rules))
    uncovered_catalog_rules = sorted(set(catalog_rules) - set(covered_rules))

    return {
        "sampling_strategy": sampling_strategy,
        "source_example_count": len(source_rows),
        "evaluation_example_count": len(dataset_rows),
        "mutation_count": len(MUTATION_REGISTRY),
        "mutations": sorted(MUTATION_REGISTRY.keys()),
        "catalog_rule_count": len(catalog_rules),
        "catalog_rules": catalog_rules,
        "covered_rule_count": len(covered_rules),
        "covered_rules": covered_rules,
        "covered_catalog_rule_count": len(covered_catalog_rules),
        "covered_catalog_rules": covered_catalog_rules,
        "extra_observed_rules": extra_observed_rules,
        "uncovered_catalog_rules": uncovered_catalog_rules,
        "source_impact_distribution": count_impacts(source_rows),
        "evaluation_impact_distribution": count_impacts(dataset_rows),
    }


def safe_generate(model, prompt):
    started = time.perf_counter()

    try:
        response = model.generate(prompt)
        elapsed = time.perf_counter() - started
        return response, elapsed, None
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return "", elapsed, {
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }


def compute_metrics(y_true, y_pred, labels):
    accuracy = accuracy_score(y_true, y_pred)
    macro = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0,
    )
    micro = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        average="micro",
        zero_division=0,
    )
    weighted = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        average="weighted",
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "precision_macro": macro[0],
        "recall_macro": macro[1],
        "f1_macro": macro[2],
        "precision_micro": micro[0],
        "recall_micro": micro[1],
        "f1_micro": micro[2],
        "precision_weighted": weighted[0],
        "recall_weighted": weighted[1],
        "f1_weighted": weighted[2],
    }


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save_confusion_matrix(y_true, y_pred, labels, title, output_path):
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    width = max(7, len(labels) * 0.65)
    height = max(5.5, len(labels) * 0.55)

    plt.figure(figsize=(width, height))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Ground truth")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def save_metrics_comparison(metrics_rows, output_path):
    metrics = ["accuracy", "f1_macro", "f1_weighted"]
    x = range(len(metrics))
    width = 0.35

    plt.figure(figsize=(8.5, 4.8))

    for index, row in enumerate(metrics_rows):
        offset = (index - 0.5) * width
        plt.bar(
            [value + offset for value in x],
            [row[metric] for metric in metrics],
            width=width,
            label=row["approach"],
        )

    plt.title("T5 validation benchmark")
    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.xticks(list(x), metrics)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def image_flowable(path, max_width=16.5 * cm, max_height=9.0 * cm):
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def styles():
    sheet = getSampleStyleSheet()
    sheet.add(ParagraphStyle(
        name="TitleCenter",
        parent=sheet["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#0B1F33"),
    ))
    sheet.add(ParagraphStyle(
        name="Section",
        parent=sheet["Heading1"],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=8,
    ))
    sheet.add(ParagraphStyle(
        name="BodySmall",
        parent=sheet["BodyText"],
        fontSize=8.5,
        leading=11,
    ))
    sheet.add(ParagraphStyle(
        name="CodeSmall",
        parent=sheet["Code"],
        fontName="Courier",
        fontSize=6.2,
        leading=7.0,
        backColor=colors.HexColor("#F8FAFC"),
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=0.25,
        borderPadding=4,
    ))
    return sheet


def truncate(value, max_chars=72):
    text = str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def table(data, col_widths=None, font_size=7.5, truncate_at=None):
    if truncate_at:
        data = [
            [truncate(cell, truncate_at) for cell in row]
            for row in data
        ]

    output = Table(data, colWidths=col_widths, repeatRows=1)
    output.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8FAFC"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return output


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf(output_dir, metrics_rows, errors, coverage_summary):
    output_dir = Path(output_dir)
    sheet = styles()
    pdf_path = output_dir / "T5_Validation_Experiment_Report.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="T5 Validation Experiment Report",
    )
    story = []

    story.append(Spacer(1, 1.8 * cm))
    story.append(Paragraph("T5-small Validation Benchmark", sheet["TitleCenter"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        sheet["BodyText"],
    ))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(
        "Comparison between the current JSON-based T5 validator and a simplified DSL "
        "prompt with 0/1/2 impact targets.",
        sheet["BodySmall"],
    ))
    story.append(PageBreak())

    story.append(Paragraph("1. Executive Summary", sheet["Section"]))
    story.append(Paragraph(
        "This experiment compares two ways of asking T5-small to validate GDPR "
        "enrichment. The baseline keeps the original verbose JSON prompt and expects "
        "a textual rule-level answer. The simplified approach removes most structural "
        "noise and asks the model to evaluate one rule over a compact trace DSL, "
        "returning only the compliance impact: 0 compliant, 1 violation or 2 warning.",
        sheet["BodySmall"],
    ))
    story.append(Spacer(1, 0.18 * cm))
    story.append(Paragraph("Baseline JSON example", sheet["BodySmall"]))
    story.append(Preformatted(
        'Input:\n'
        'validate gdpr enrichment: {"traceId":"case_0","context":{"legalBasis":"consent"},'
        '"events":[{"activityType":"CASE_START"},{"activityType":"DATA_COLLECTION"}]}\n\n'
        'Expected output:\n'
        'invalid | violations: DATA_COLLECTION_CONSENT_REQUIRED@trace | warnings: none',
        sheet["CodeSmall"],
    ))
    story.append(Spacer(1, 0.12 * cm))
    story.append(Paragraph("Simplified DSL example", sheet["BodySmall"]))
    story.append(Preformatted(
        "Input:\n"
        "validate gdpr impact: rule: DATA_COLLECTION | context: legal_basis:consent | "
        "trace: CASE_START -> DATA_COLLECTION | return only 0, 1 or 2\n\n"
        "Expected output:\n"
        "1",
        sheet["CodeSmall"],
    ))
    story.append(Spacer(1, 0.3 * cm))
    summary_rows = [[
        "Approach",
        "Accuracy",
        "F1 Macro",
        "F1 Weighted",
        "Avg latency (s)",
        "Errors",
    ]]
    for row in metrics_rows:
        summary_rows.append([
            row["approach"],
            f"{row['accuracy']:.3f}",
            f"{row['f1_macro']:.3f}",
            f"{row['f1_weighted']:.3f}",
            f"{row['avg_latency_seconds']:.3f}",
            str(row["error_count"]),
        ])
    story.append(table(summary_rows, [4.0 * cm, 2.3 * cm, 2.4 * cm, 2.7 * cm, 2.6 * cm, 1.8 * cm]))
    story.append(Spacer(1, 0.35 * cm))
    coverage_rows = [
        ["Sampling strategy", coverage_summary["sampling_strategy"]],
        ["Source examples", str(coverage_summary["source_example_count"])],
        ["Evaluated examples", str(coverage_summary["evaluation_example_count"])],
        ["Registered mutations", str(coverage_summary["mutation_count"])],
        ["Catalogued deterministic rules", str(coverage_summary["catalog_rule_count"])],
        ["Catalogued rules covered by evaluated examples", str(coverage_summary["covered_catalog_rule_count"])],
        ["Extra observed warning/rule labels", str(len(coverage_summary["extra_observed_rules"]))],
        ["Source impact distribution", json.dumps(coverage_summary["source_impact_distribution"])],
        ["Evaluation impact distribution", json.dumps(coverage_summary["evaluation_impact_distribution"])],
    ]
    story.append(table(
        [["Coverage item", "Value"]] + coverage_rows,
        [6.5 * cm, 9.5 * cm],
        font_size=6.7,
        truncate_at=86,
    ))
    story.append(Spacer(1, 0.35 * cm))
    story.append(image_flowable(output_dir / "t5_metrics_comparison.png", max_height=7.5 * cm))
    story.append(PageBreak())

    story.append(Paragraph("2. Confusion Matrices", sheet["Section"]))
    image_table = Table(
        [
            [
                Paragraph("Baseline JSON - impact view", sheet["BodySmall"]),
                Paragraph("Simplified DSL - strict impact view", sheet["BodySmall"]),
            ],
            [
                image_flowable(output_dir / "t5_baseline_confusion_matrix.png", max_width=7.8 * cm, max_height=7.2 * cm),
                image_flowable(output_dir / "t5_simplified_confusion_matrix.png", max_width=7.8 * cm, max_height=7.2 * cm),
            ],
        ],
        colWidths=[8.0 * cm, 8.0 * cm],
    )
    image_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(image_table)
    story.append(PageBreak())

    story.append(Paragraph("3. Classification Reports", sheet["Section"]))
    for filename, title in [
        ("t5_baseline_classification_report.txt", "Baseline JSON classification report"),
        ("t5_simplified_classification_report.txt", "Simplified DSL classification report"),
    ]:
        story.append(Paragraph(title, sheet["BodySmall"]))
        story.append(Preformatted(
            (output_dir / filename).read_text(encoding="utf-8"),
            sheet["CodeSmall"],
        ))
    story.append(PageBreak())

    story.append(Paragraph("4. Prediction Appendix", sheet["Section"]))
    story.append(Paragraph(
        "Representative rows prioritise errors and disagreements between ground truth and prediction.",
        sheet["BodySmall"],
    ))

    for filename, title in [
        ("t5_baseline_impact_predictions.csv", "Baseline JSON impact sample"),
        ("t5_simplified_predictions.csv", "Simplified DSL sample"),
    ]:
        rows = load_csv(output_dir / filename)
        rows.sort(key=lambda row: (row.get("is_correct") == "True", row.get("rule_evaluated", "")))
        sample = rows[:24]
        table_rows = [["Trace", "Rule", "y_true", "y_pred", "Correct"]]
        for row in sample:
            table_rows.append([
                row["trace_id"],
                row["rule_evaluated"],
                row["y_true"],
                row["y_pred"],
                row["is_correct"],
            ])
        story.append(Paragraph(title, sheet["BodySmall"]))
        story.append(table(
            table_rows,
            [2.2 * cm, 5.2 * cm, 3.3 * cm, 3.3 * cm, 1.8 * cm],
            font_size=6.0,
            truncate_at=48,
        ))
        story.append(Spacer(1, 0.3 * cm))

    story.append(PageBreak())
    story.append(Paragraph("5. Conclusion", sheet["Section"]))
    best = max(metrics_rows, key=lambda row: row["f1_weighted"])
    baseline = next(row for row in metrics_rows if row["approach"] == "baseline_json")
    simplified = next(row for row in metrics_rows if row["approach"] == "simplified_dsl")

    conclusion = (
        f"The best weighted F1 in this run is obtained by {best['approach']} "
        f"({best['f1_weighted']:.3f}). The simplified DSL approach is designed to "
        "reduce input noise and collapse outputs into direct compliance impact labels. "
        f"In this benchmark, baseline weighted F1 is {baseline['f1_weighted']:.3f} "
        f"and simplified weighted F1 is {simplified['f1_weighted']:.3f}."
    )
    story.append(Paragraph(conclusion, sheet["BodySmall"]))

    if errors:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"{len(errors)} inference error(s) were captured. See t5_error_log.json.",
            sheet["BodySmall"],
        ))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return pdf_path


def evaluate(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    examples = load_examples(args.data_dir, args.split)

    if args.max_examples and args.max_examples > 0:
        examples = examples[:args.max_examples]

    source_rows = build_dataset_rows(examples)
    sampling_strategy = "natural"

    if args.no_balance_impact:
        dataset_rows = source_rows
    else:
        dataset_rows = balance_rows_by_impact(source_rows)
        sampling_strategy = "impact_balanced"

    coverage_summary = build_coverage_summary(
        dataset_rows,
        source_rows=source_rows,
        sampling_strategy=sampling_strategy,
    )
    baseline_model_path = Path(args.baseline_model)
    simplified_model_path = Path(args.simplified_model) if args.simplified_model else baseline_model_path

    baseline_model = T5Client(str(baseline_model_path))

    if simplified_model_path == baseline_model_path:
        simplified_model = baseline_model
    else:
        simplified_model = T5Client(str(simplified_model_path))

    baseline_predictions = []
    baseline_impact_predictions = []
    simplified_predictions = []
    errors = []

    for row in dataset_rows:
        response, latency, error = safe_generate(baseline_model, row["baseline_input"])
        rule_y_pred = "INFERENCE_ERROR" if error else parse_baseline_prediction(response)
        impact_y_pred = "INFERENCE_ERROR" if error else parse_baseline_impact_prediction(response)
        rule_is_correct = rule_y_pred == row["baseline_y_true"]
        impact_is_correct = impact_y_pred == row["simplified_y_true"]

        baseline_predictions.append({
            "trace_id": row["trace_id"],
            "rule_evaluated": row["rule_evaluated"],
            "y_true": row["baseline_y_true"],
            "y_pred": rule_y_pred,
            "is_correct": rule_is_correct,
            "latency_seconds": f"{latency:.6f}",
            "raw_response": response,
            "input_text": row["baseline_input"],
        })
        baseline_impact_predictions.append({
            "trace_id": row["trace_id"],
            "rule_evaluated": row["rule_evaluated"],
            "y_true": row["simplified_y_true"],
            "y_pred": impact_y_pred,
            "is_correct": impact_is_correct,
            "latency_seconds": f"{latency:.6f}",
            "raw_response": response,
            "input_text": row["baseline_input"],
        })

        if error:
            errors.append({
                "approach": "baseline_json",
                "trace_id": row["trace_id"],
                "rule_evaluated": row["rule_evaluated"],
                **error,
            })

        response, latency, error = safe_generate(simplified_model, row["simplified_input"])
        y_pred = "INFERENCE_ERROR" if error else parse_simplified_prediction(response)
        is_correct = y_pred == row["simplified_y_true"]

        simplified_predictions.append({
            "trace_id": row["trace_id"],
            "rule_evaluated": row["rule_evaluated"],
            "y_true": row["simplified_y_true"],
            "y_pred": y_pred,
            "is_correct": is_correct,
            "latency_seconds": f"{latency:.6f}",
            "raw_response": response,
            "input_text": row["simplified_input"],
        })

        if error:
            errors.append({
                "approach": "simplified_dsl",
                "trace_id": row["trace_id"],
                "rule_evaluated": row["rule_evaluated"],
                **error,
            })

    prediction_fields = [
        "trace_id",
        "rule_evaluated",
        "y_true",
        "y_pred",
        "is_correct",
        "latency_seconds",
        "raw_response",
        "input_text",
    ]
    write_csv(output_dir / "t5_baseline_predictions.csv", baseline_predictions, prediction_fields)
    write_csv(output_dir / "t5_baseline_impact_predictions.csv", baseline_impact_predictions, prediction_fields)
    write_csv(output_dir / "t5_simplified_predictions.csv", simplified_predictions, prediction_fields)
    write_csv(
        output_dir / "t5_simplified_dsl_dataset.csv",
        [
            {
                "trace_id": row["trace_id"],
                "rule_evaluated": row["rule_evaluated"],
                "impact_label": row["simplified_y_true"],
                "sampling_strategy": row.get("sampling_strategy", sampling_strategy),
                "split": row["split"],
                "source_file": row["source_file"],
                "dsl_input": row["simplified_input"],
                "baseline_target": row["baseline_target"],
            }
            for row in dataset_rows
        ],
        [
            "trace_id",
            "rule_evaluated",
            "impact_label",
            "sampling_strategy",
            "split",
            "source_file",
            "dsl_input",
            "baseline_target",
        ],
    )

    metrics_rows = []

    baseline_rule_labels = sorted({
        row["y_true"]
        for row in baseline_predictions
    } | {
        row["y_pred"]
        for row in baseline_predictions
    })
    baseline_rule_y_true = [row["y_true"] for row in baseline_predictions]
    baseline_rule_y_pred = [row["y_pred"] for row in baseline_predictions]
    (output_dir / "t5_baseline_rule_classification_report.txt").write_text(
        classification_report(
            baseline_rule_y_true,
            baseline_rule_y_pred,
            labels=baseline_rule_labels,
            zero_division=0,
        ),
        encoding="utf-8",
    )
    save_confusion_matrix(
        baseline_rule_y_true,
        baseline_rule_y_pred,
        baseline_rule_labels,
        "baseline_json detailed rule confusion matrix",
        output_dir / "t5_baseline_rule_confusion_matrix.png",
    )

    for approach, predictions, labels, report_name, matrix_name in [
        (
            "baseline_json",
            baseline_impact_predictions,
            IMPACT_LABELS
            + sorted({
                row["y_pred"]
                for row in baseline_impact_predictions
                if row["y_pred"] not in IMPACT_LABELS
            }),
            "t5_baseline_classification_report.txt",
            "t5_baseline_confusion_matrix.png",
        ),
        (
            "simplified_dsl",
            simplified_predictions,
            IMPACT_LABELS
            + sorted({
                row["y_pred"]
                for row in simplified_predictions
                if row["y_pred"] not in IMPACT_LABELS
            }),
            "t5_simplified_classification_report.txt",
            "t5_simplified_confusion_matrix.png",
        ),
    ]:
        y_true = [row["y_true"] for row in predictions]
        y_pred = [row["y_pred"] for row in predictions]
        metrics = compute_metrics(y_true, y_pred, labels)
        avg_latency = sum(float(row["latency_seconds"]) for row in predictions) / max(len(predictions), 1)
        error_count = sum(1 for row in predictions if row["y_pred"] == "INFERENCE_ERROR")
        metrics_rows.append({
            "approach": approach,
            **metrics,
            "avg_latency_seconds": avg_latency,
            "error_count": error_count,
        })

        report_text = classification_report(
            y_true,
            y_pred,
            labels=labels,
            zero_division=0,
        )
        (output_dir / report_name).write_text(report_text, encoding="utf-8")
        save_confusion_matrix(
            y_true,
            y_pred,
            labels,
            f"{approach} confusion matrix",
            output_dir / matrix_name,
        )

    write_csv(
        output_dir / "t5_metrics_summary.csv",
        metrics_rows,
        [
            "approach",
            "accuracy",
            "precision_macro",
            "recall_macro",
            "f1_macro",
            "precision_micro",
            "recall_micro",
            "f1_micro",
            "precision_weighted",
            "recall_weighted",
            "f1_weighted",
            "avg_latency_seconds",
            "error_count",
        ],
    )
    save_metrics_comparison(metrics_rows, output_dir / "t5_metrics_comparison.png")

    (output_dir / "t5_error_log.json").write_text(
        json.dumps(errors, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "t5_experiment_metadata.json").write_text(
        json.dumps({
            "split": args.split,
            "example_count": len(dataset_rows),
            "baseline_model": str(baseline_model_path),
            "simplified_model": str(simplified_model_path),
            "data_dir": str(Path(args.data_dir)),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "coverage": coverage_summary,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    pdf_path = generate_pdf(output_dir, metrics_rows, errors, coverage_summary)

    print(f"T5 benchmark completed. Results written to: {output_dir}")
    print(f"Executive PDF report written to: {pdf_path}")


if __name__ == "__main__":
    evaluate(parse_args())
