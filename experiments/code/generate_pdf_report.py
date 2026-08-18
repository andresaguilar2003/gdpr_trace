import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = ROOT / "experiments" / "results"
DEFAULT_OUTPUT_PATH = DEFAULT_RESULTS_DIR / "Executive_Experiment_Report.pdf"

CONTEXT_ACCEPTABLE_KEYWORDS = {
    "medical_treatment": [
        "medical",
        "health",
        "healthcare",
        "hospital",
        "clinical",
        "patient",
        "treatment",
        "sepsis",
    ],
    "contract_execution": [
        "contract",
        "loan",
        "credit",
        "application",
        "offer",
        "banking",
        "financial",
        "service_delivery",
    ],
    "legal_obligation": [
        "legal_obligation",
        "legal",
        "obligation",
        "compliance",
        "required_by_law",
        "regulation",
    ],
    "contract": [
        "contract",
        "loan",
        "credit",
        "application",
        "customer",
        "banking",
    ],
    "health": [
        "health",
        "medical",
        "clinical",
        "hospital",
        "patient",
        "special_categories",
        "special_category",
        "sepsis",
    ],
    "standard": [
        "standard",
        "personal",
        "customer",
        "applicant",
        "financial",
        "banking",
    ],
    "patient": [
        "patient",
        "data_subject",
        "individual",
        "person",
    ],
    "customer": [
        "customer",
        "client",
        "applicant",
        "borrower",
        "data_subject",
    ],
    "legal_requirement": [
        "legal_requirement",
        "required_by_law",
        "regulation",
        "compliance",
        "healthcare",
        "medical",
    ],
    "indefinite": [
        "indefinite",
        "necessary",
        "as_long_as_necessary",
        "retained",
        "business_need",
    ],
    "healthcare": [
        "healthcare",
        "health",
        "medical",
        "hospital",
        "clinical",
        "patient",
        "sepsis",
    ],
    "banking": [
        "banking",
        "bank",
        "financial",
        "finance",
        "loan",
        "credit",
        "lending",
    ],
    "false": [
        "false",
        "no",
        "none",
        "not_applicable",
        "not_needed",
    ],
    "none": [
        "none",
        "no",
        "not_applicable",
        "not_needed",
        "no_transfer",
        "no_safeguard",
    ],
    "not_needed": [
        "not_needed",
        "not_required",
        "none",
        "no",
    ],
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a single executive PDF report from model evaluation results."
    )
    parser.add_argument(
        "--results-dir",
        default=str(DEFAULT_RESULTS_DIR),
        help="Directory containing metrics_summary.csv, evaluation_results.json and PNG figures.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output PDF path.",
    )
    return parser.parse_args()


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path):
    if not path.exists():
        return {}

    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def metric_value(row, key):
    try:
        return f"{float(row.get(key, 0.0)):.3f}"
    except (TypeError, ValueError):
        return "n/a"


def normalize_token(value):
    return str(value or "").strip().lower().replace(" ", "_")


def acceptable_context_values(expected_value, row=None):
    row = row or {}
    explicit_values = row.get("acceptable_values")

    if explicit_values:
        return explicit_values

    expected = normalize_token(expected_value)
    keywords = CONTEXT_ACCEPTABLE_KEYWORDS.get(expected, [])
    values = [expected] + [
        keyword
        for keyword in keywords
        if keyword != expected
    ]

    return " | ".join(values)


def format_context_ground_truth(expected_value, row=None, max_keywords=5):
    accepted = acceptable_context_values(expected_value, row)
    accepted_values = [
        value.strip()
        for value in accepted.split("|")
        if value.strip()
    ]

    if not accepted_values:
        return str(expected_value)

    canonical = accepted_values[0]
    alternatives = accepted_values[1:max_keywords + 1]

    if not alternatives:
        return canonical

    return f"{canonical} (valid: {', '.join(alternatives)})"


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B1F33"),
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["BodyText"],
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading1"],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=10,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=6.4,
        leading=7.2,
        textColor=colors.HexColor("#111827"),
        backColor=colors.HexColor("#F8FAFC"),
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=0.25,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=8,
    ))

    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawRightString(
        A4[0] - 1.5 * cm,
        1.0 * cm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def make_table(rows, header, widths=None):
    table = Table([header] + rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F8FAFC"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def make_compact_table(rows, header, widths=None):
    paragraph_style = ParagraphStyle(
        name="CellSmall",
        fontName="Helvetica",
        fontSize=6.4,
        leading=7.5,
        textColor=colors.HexColor("#111827"),
    )
    header_style = ParagraphStyle(
        name="HeaderSmall",
        fontName="Helvetica-Bold",
        fontSize=6.6,
        leading=7.5,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    prepared = [
        [Paragraph(str(value), header_style) for value in header]
    ]

    for row in rows:
        prepared.append([
            Paragraph(str(value), paragraph_style)
            for value in row
        ])

    table = Table(prepared, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
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
    return table


def image_flowable(path, max_width=16.5 * cm, max_height=10.5 * cm):
    if not path.exists():
        return Paragraph(
            f"Missing image: {path.name}",
            build_styles()["Small"],
        )

    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def image_pair_table(
    left_title,
    left_path,
    right_title,
    right_path,
    styles,
    max_image_width=7.6 * cm,
    max_image_height=6.6 * cm,
):
    table = Table(
        [
            [
                Paragraph(left_title, styles["Small"]),
                Paragraph(right_title, styles["Small"]),
            ],
            [
                image_flowable(left_path, max_image_width, max_image_height),
                image_flowable(right_path, max_image_width, max_image_height),
            ],
        ],
        colWidths=[8.0 * cm, 8.0 * cm],
    )
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


def build_summary_rows(metrics_rows):
    ordered = sorted(metrics_rows, key=lambda row: (row["task"], row["model"]))
    return [
        [
            row["task"],
            row["model"],
            metric_value(row, "accuracy"),
            metric_value(row, "f1_macro"),
            metric_value(row, "f1_weighted"),
        ]
        for row in ordered
    ]


def best_global_model(metrics_rows):
    scores = {}

    for row in metrics_rows:
        model = row["model"]
        try:
            value = float(row.get("f1_weighted", 0.0))
        except (TypeError, ValueError):
            value = 0.0
        scores.setdefault(model, []).append(value)

    averages = {
        model: sum(values) / len(values)
        for model, values in scores.items()
        if values
    }

    if not averages:
        return "n/a", 0.0, averages

    model = max(averages, key=averages.get)
    return model, averages[model], averages


def read_text(path):
    path = Path(path)
    if not path.exists():
        return f"Missing file: {path.name}"

    return path.read_text(encoding="utf-8", errors="replace").strip()


def append_classification_reports(story, results_dir, styles, task_prefix, title):
    story.append(Paragraph(title, styles["Small"]))

    for model in ["phi3", "roberta"]:
        report_path = results_dir / f"{task_prefix}_{model}_classification_report.txt"
        story.append(Paragraph(f"{model.upper()} classification report", styles["Small"]))
        story.append(Preformatted(read_text(report_path), styles["CodeBlock"]))


def build_prediction_comparison_rows(
    csv_path,
    item_column,
    max_rows=24,
    truth_column="y_true",
    prediction_column="y_pred",
    truth_formatter=None,
):
    rows = load_csv(csv_path)
    grouped = {}

    for row in rows:
        truth_value = row.get(truth_column, row.get("y_true", ""))
        truth_display = (
            truth_formatter(truth_value, row)
            if truth_formatter
            else truth_value
        )
        key = (
            row.get("dataset", ""),
            row.get(item_column, ""),
            truth_display,
        )
        grouped.setdefault(key, {})
        grouped[key][row.get("model", "")] = {
            "display": row.get(prediction_column, row.get("y_pred", "")),
            "impact": row.get("y_pred", ""),
        }

    comparison_rows = []

    for (dataset, item, y_true), predictions in grouped.items():
        phi3_data = predictions.get("phi3", {})
        roberta_data = predictions.get("roberta", {})
        phi3 = phi3_data.get("display", "n/a")
        roberta = roberta_data.get("display", "n/a")
        phi3_impact = phi3_data.get("impact", "")
        roberta_impact = roberta_data.get("impact", "")
        has_disagreement = (
            phi3 != roberta
            or phi3 != y_true
            or roberta != y_true
            or phi3_impact not in {"", "0_COMPLIANT"}
            or roberta_impact not in {"", "0_COMPLIANT"}
        )

        comparison_rows.append({
            "dataset": dataset,
            "item": item,
            "y_true": y_true,
            "phi3": phi3,
            "roberta": roberta,
            "has_disagreement": has_disagreement,
        })

    comparison_rows.sort(
        key=lambda row: (
            not row["has_disagreement"],
            row["dataset"],
            row["item"],
        )
    )

    selected = comparison_rows[:max_rows]

    return [
        [
            row["dataset"],
            row["item"],
            row["y_true"],
            row["phi3"],
            row["roberta"],
        ]
        for row in selected
    ]


def generate_pdf_report(results_dir=DEFAULT_RESULTS_DIR, output_path=DEFAULT_OUTPUT_PATH):
    results_dir = Path(results_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metrics_path = results_dir / "metrics_summary.csv"
    if not metrics_path.exists():
        raise FileNotFoundError(f"Required file not found: {metrics_path}")

    metrics_rows = load_csv(metrics_path)
    evaluation = load_json(results_dir / "evaluation_results.json")
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Executive Experiment Report",
    )

    story = []
    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    story.append(Spacer(1, 2.0 * cm))
    story.append(Paragraph("Phi-3 vs RoBERTa Evaluation", styles["CoverTitle"]))
    story.append(Paragraph("Executive Experiment Report", styles["CoverSubtitle"]))
    story.append(Paragraph(f"Generated on: {run_date}", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "Objective: compare the previous Phi-3 inference pipeline against the current "
        "RoBERTa pipeline for GDPR dataset-context inference and ActivityType classification "
        "over real Process Mining event logs.",
        styles["Body"],
    ))

    datasets = evaluation.get("datasets", {})
    if datasets:
        dataset_rows = [
            [
                name,
                str(info.get("trace_count", "n/a")),
                str(info.get("activity_count", "n/a")),
                Path(info.get("path", "")).name,
            ]
            for name, info in datasets.items()
        ]
        story.append(Spacer(1, 0.3 * cm))
        story.append(make_table(
            dataset_rows,
            ["Dataset", "Traces", "Activities", "Source file"],
            widths=[3.0 * cm, 2.0 * cm, 2.2 * cm, 8.5 * cm],
        ))

    story.append(PageBreak())

    story.append(Paragraph("1. Executive Summary", styles["SectionTitle"]))
    story.append(Paragraph(
        "The table below consolidates the key metrics from the two evaluated tasks: "
        "global context inference and individual activity typing.",
        styles["Body"],
    ))
    story.append(make_table(
        build_summary_rows(metrics_rows),
        ["Task", "Model", "Accuracy", "F1 Macro", "F1 Weighted"],
        widths=[3.6 * cm, 3.0 * cm, 2.5 * cm, 2.7 * cm, 2.9 * cm],
    ))

    story.append(PageBreak())

    story.append(Paragraph("2. Context Analysis", styles["SectionTitle"]))
    story.append(Paragraph(
        "This section evaluates how each model fills the GDPR Context attributes such as "
        "purpose, legal basis, data category, data subject type, processing domain and "
        "transfer-related metadata. Context outputs are evaluated with flexible keyword "
        "matching and collapsed into regulatory impact classes: 0_COMPLIANT, "
        "1_VIOLATION and 2_WARNING.",
        styles["Body"],
    ))
    story.append(image_flowable(
        results_dir / "context_metrics_comparison.png",
        max_height=7.5 * cm,
    ))
    story.append(Spacer(1, 0.25 * cm))
    story.append(image_pair_table(
        "Context confusion matrix - Phi-3",
        results_dir / "context_phi3_confusion_matrix.png",
        "Context confusion matrix - RoBERTa",
        results_dir / "context_roberta_confusion_matrix.png",
        styles,
        max_image_height=7.2 * cm,
    ))
    story.append(Spacer(1, 0.2 * cm))
    append_classification_reports(
        story,
        results_dir,
        styles,
        task_prefix="context",
        title="Detailed context impact classification reports",
    )

    story.append(PageBreak())

    story.append(Paragraph("3. Activity Typing Analysis", styles["SectionTitle"]))
    story.append(Paragraph(
        "This section evaluates the mapping of process-mining event labels to the controlled "
        "ActivityType enum used by the enrichment engine.",
        styles["Body"],
    ))
    story.append(KeepTogether([
        image_flowable(
            results_dir / "activity_type_metrics_comparison.png",
            max_height=7.0 * cm,
        ),
        Spacer(1, 0.25 * cm),
        image_pair_table(
            "ActivityType confusion matrix - Phi-3",
            results_dir / "activity_type_phi3_confusion_matrix.png",
            "ActivityType confusion matrix - RoBERTa",
            results_dir / "activity_type_roberta_confusion_matrix.png",
            styles,
            max_image_height=8.0 * cm,
        ),
    ]))
    story.append(Spacer(1, 0.2 * cm))
    append_classification_reports(
        story,
        results_dir,
        styles,
        task_prefix="activity_type",
        title="Detailed ActivityType classification reports",
    )

    story.append(PageBreak())

    story.append(Paragraph("4. Prediction Appendix", styles["SectionTitle"]))
    story.append(Paragraph(
        "The following tables show a representative audit sample from the raw prediction CSVs. "
        "Rows with model disagreement or errors are prioritised so that failure modes can be "
        "inspected without turning the PDF into a full data dump.",
        styles["Body"],
    ))

    context_prediction_rows = build_prediction_comparison_rows(
        results_dir / "context_predictions.csv",
        item_column="field",
        truth_column="expected_value",
        prediction_column="predicted_value",
        truth_formatter=format_context_ground_truth,
        max_rows=24,
    )
    story.append(Paragraph("Context predictions sample", styles["Small"]))
    story.append(make_compact_table(
        context_prediction_rows,
        ["Dataset", "Field", "Ground Truth", "Phi-3", "RoBERTa"],
        widths=[1.8 * cm, 2.8 * cm, 5.2 * cm, 3.5 * cm, 3.5 * cm],
    ))

    story.append(Spacer(1, 0.35 * cm))

    activity_prediction_rows = build_prediction_comparison_rows(
        results_dir / "activity_predictions.csv",
        item_column="activity",
        max_rows=28,
    )
    story.append(Paragraph("ActivityType predictions sample", styles["Small"]))
    story.append(make_compact_table(
        activity_prediction_rows,
        ["Dataset", "Activity / Field", "Ground Truth", "Phi-3", "RoBERTa"],
        widths=[2.0 * cm, 4.8 * cm, 3.5 * cm, 3.2 * cm, 3.2 * cm],
    ))

    story.append(PageBreak())

    story.append(Paragraph("5. Conclusion", styles["SectionTitle"]))
    best_model, best_score, averages = best_global_model(metrics_rows)
    roberta_score = averages.get("roberta")
    phi3_score = averages.get("phi3")

    if roberta_score is not None and phi3_score is not None and roberta_score >= phi3_score:
        conclusion = (
            f"RoBERTa obtains the best global weighted F1 score ({roberta_score:.3f}) "
            f"against Phi-3 ({phi3_score:.3f}). This supports the working hypothesis: "
            "RoBERTa provides a more stable regulatory classification layer because it "
            "uses constrained zero-shot classification plus domain heuristics instead of "
            "free-form JSON generation."
        )
    elif roberta_score is not None and phi3_score is not None:
        conclusion = (
            f"Phi-3 obtains the highest global weighted F1 score ({phi3_score:.3f}) "
            f"against RoBERTa ({roberta_score:.3f}) in this run. Even so, RoBERTa remains "
            "operationally attractive for regulatory stability because its predictions are "
            "constrained to explicit labels and are less exposed to malformed generative output."
        )
    else:
        conclusion = (
            f"The best available model in this run is {best_model} with global weighted F1 "
            f"{best_score:.3f}. If Phi-3 was skipped or failed, the report should be read as "
            "a RoBERTa-only validation run."
        )

    story.append(Paragraph(conclusion, styles["Body"]))

    errors = evaluation.get("errors", [])
    if errors:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"Execution note: {len(errors)} model execution error(s) were recorded. "
            "See evaluation_results.json for full tracebacks.",
            styles["Small"],
        ))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return output_path


if __name__ == "__main__":
    args = parse_args()
    path = generate_pdf_report(args.results_dir, args.output)
    print(f"PDF report written to: {path}")
