import argparse
import csv
import hashlib
import html
import json
import re
import sys
import textwrap
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
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
RULES_MD = ROOT / "app" / "validation" / "rules.md"
RULES_PDF = ROOT / "app" / "validation" / "rules.pdf"
VALIDATOR_PY = ROOT / "app" / "validation" / "validators" / "gdpr_enrichment_validator.py"
OUTPUT_DIR = ROOT / "experiments" / "results"
REPORT_PATH = OUTPUT_DIR / "OCL_Rules_Optimization_Report.pdf"

ACTIVITY_TYPES = [
    "CASE_START",
    "DATA_COLLECTION",
    "DATA_ACCESS",
    "DATA_PROCESSING",
    "AUTOMATED_DECISION",
    "DATA_TRANSFER",
    "STORAGE_MANAGEMENT",
    "USER_RIGHT_REQUEST",
    "DATA_DELETION",
    "CASE_END",
    "GDPR_COMPLIANCE",
    "OTHER",
]

CONTROL_EVENTS = [
    "verify_legal_basis",
    "privacy_notice_disclosed",
    "check_consent",
    "record_purpose",
    "minimisation_check",
    "encryption_applied",
    "log_processing_activity",
    "access_control_check",
    "check_third_party_agreement",
    "verify_international_safeguard",
    "automated_logic_disclosure",
    "verify_request_identity",
    "respond_user_right",
    "provide_data_copy",
    "update_primary_record",
    "propagate_rectification_to_replicas",
    "notify_data_rectification_to_recipients",
    "verify_rectification_consistency",
    "erase_primary_record",
    "propagate_erasure_to_replicas",
    "notify_third_party_deletion",
    "verify_erasure_completion",
    "verify_restriction_lift_conditions",
    "mark_data_as_restricted",
    "generate_interoperable_format",
    "transmit_to_new_controller",
    "verify_compelling_legitimate_grounds",
    "halt_processing_activities",
    "contest_automated_decision",
    "provide_transparency_details",
    "record_retention_period",
    "retention_period_verify",
    "confirm_data_erasure",
    "erase_data",
]

CONTEXT_TERMS = [
    "legal_basis",
    "data_category",
    "retention_period",
    "has_third_party_recipients",
    "international_transfer",
    "transfer_safeguard",
    "consent_status",
    "purpose",
    "data_subject_type",
    "user_right_type",
]


@dataclass
class RuleRecord:
    name: str
    ocl: str
    source: str
    events: list[str] = field(default_factory=list)
    context_terms: list[str] = field(default_factory=list)
    temporal_terms: list[str] = field(default_factory=list)
    complexity: int = 0
    coverage_score: float = 0.0
    status: str = "CORRECTA"
    merge_group: str = ""
    origin_rules: list[str] = field(default_factory=list)
    finding: str = ""
    optimized_ocl: str = ""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit, optimize, and report GDPR OCL rules with optional Phi-4-mini support."
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "transformers", "none"],
        default="auto",
        help="Use Phi-4-mini through Transformers when available, or force the deterministic auditor.",
    )
    parser.add_argument(
        "--model-id",
        default="microsoft/Phi-4-mini-instruct",
        help="Hugging Face model id for Phi-4-mini.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=900,
        help="Maximum generated tokens for the optional LLM audit.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directory where JSON, CSV, charts, and PDF will be written.",
    )
    return parser.parse_args()


def read_rule_source():
    if RULES_PDF.exists():
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(RULES_PDF))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
            if text:
                return text, str(RULES_PDF)
        except Exception:
            pass

    if RULES_MD.exists():
        return RULES_MD.read_text(encoding="utf-8", errors="ignore"), str(RULES_MD)

    return VALIDATOR_PY.read_text(encoding="utf-8", errors="ignore"), str(VALIDATOR_PY)


def clean_rules_text(text):
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</span>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_ocl_rules_from_text(text, source):
    clean = clean_rules_text(text)
    pattern = re.compile(
        r"(context\s+Trace\s+inv\s+([A-Z0-9_]+)\s*:\s*.*?)(?=\n\s*context\s+Trace\s+inv\s+[A-Z0-9_]+\s*:|\n\s*#{1,6}\s+(?:RULE:|[A-Z]\.|Cap|##)|\Z)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    records = []
    seen = set()

    for match in pattern.finditer(clean):
        ocl = normalize_ocl_block(match.group(1))
        name = match.group(2).upper()
        if name in seen:
            continue
        seen.add(name)
        records.append(RuleRecord(name=name, ocl=ocl, source=source))

    if records:
        return records

    inv_pattern = re.compile(
        r"inv\s+([A-Z0-9_]+)\s*:\s*(.*?)(?=\n\s*inv\s+[A-Z0-9_]+\s*:|\Z)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in inv_pattern.finditer(clean):
        name = match.group(1).upper()
        ocl = normalize_ocl_block("context Trace\ninv " + name + ":\n" + match.group(2))
        records.append(RuleRecord(name=name, ocl=ocl, source=source))

    return records


def extract_rules_from_validator():
    source = VALIDATOR_PY.read_text(encoding="utf-8", errors="ignore")
    records = {}

    for match in re.finditer(r'"rule"\s*:\s*"([^"]+)"', source):
        name = match.group(1).upper()
        start = max(0, match.start() - 900)
        end = min(len(source), match.end() + 1300)
        block = source[start:end]
        event_match = re.search(r'"event"\s*:\s*([^,\n}]+)', block)
        message_match = re.search(r'"message"\s*:\s*([^,\n}]+)', block)
        event = event_match.group(1).strip().strip('"') if event_match else "trace"
        message = message_match.group(1).strip().strip('"') if message_match else ""
        synthetic_ocl = validator_rule_to_ocl(name, event, message, block)
        records[name] = RuleRecord(
            name=name,
            ocl=synthetic_ocl,
            source=str(VALIDATOR_PY),
        )

    return list(records.values())


def validator_rule_to_ocl(name, event, message, block):
    event_type = infer_primary_event(name, block + " " + event)
    requirements = sorted(set(re.findall(r"'([a-zA-Z_]+)'", block)))
    if not requirements:
        requirements = [item for item in CONTROL_EVENTS if item in block]

    lines = ["context Trace", f"inv {name}:"]
    if event_type:
        lines.append(f"    for all e where e.type = {event_type}:")
    else:
        lines.append("    for all e in events:")

    if "FORBIDDEN" in name or "should NOT exist" in block:
        req = requirements[0] if requirements else "forbidden_control_event"
        lines.append(f"        not exists g where g.name = {req}")
    elif "DUPLICATED" in name:
        req = requirements[0] if requirements else "duplicated_control_event"
        lines.append(f"        events where name = {req} count <= 1")
    elif "MISSING" in name and "CONTEXT" in name:
        ctx = first_present(CONTEXT_TERMS, block) or "required_context_attribute"
        lines.append(f"        context.{ctx} is not undefined")
    else:
        req = requirements[0] if requirements else "required_control_event"
        direction = "BEFORE" if "BEFORE" in block or "before" in message.lower() else "AFTER"
        comparator = "<" if direction == "BEFORE" else ">"
        lines.append("        exists g where")
        lines.append(f"            g.name = {req} AND")
        lines.append(f"            g.position = {direction} AND")
        lines.append(f"            g.order {comparator} e.order")

    return "\n".join(lines)


def normalize_ocl_block(block):
    lines = []
    has_inv = False
    stop_markers = (
        "RULE:",
        "Objetivo",
        "Objetivo RGPD",
        "Articulos",
        "Artículos",
        "Warnings",
        "WARNING:",
        "No Criticas",
        "No Críticas",
        "Proposito",
        "Propósito",
        "Las siguientes",
        "Estas situaciones",
        "En su lugar",
        "Las advertencias",
    )
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("```") or line.lower() == "object constraint language":
            continue
        if has_inv and line.startswith(stop_markers):
            break
        if has_inv and re.match(r"^(\d+\.\s|[A-Z]\.\s|#{1,6}\s)", line):
            break
        if line.lower().startswith("inv "):
            has_inv = True
        lines.append(line)
    return "\n".join(lines)


def first_present(candidates, text):
    lowered = text.lower()
    for candidate in candidates:
        if candidate.lower() in lowered:
            return candidate
    return ""


def infer_primary_event(rule_name, text):
    upper = (rule_name + " " + text).upper()
    for activity_type in ACTIVITY_TYPES:
        if activity_type in upper:
            return activity_type
    return ""


def merge_sources(primary_records, fallback_records):
    by_name = {record.name: record for record in primary_records}
    for record in fallback_records:
        if record.name not in by_name:
            by_name[record.name] = record
        else:
            by_name[record.name].source = f"{by_name[record.name].source}; {record.source}"
    return list(by_name.values())


def enrich_rule_features(records):
    for record in records:
        feature_text = f"{record.name}\n{record.ocl}"
        upper = feature_text.upper()
        lower = feature_text.lower()

        events = [event for event in ACTIVITY_TYPES if event in upper]
        controls = [event for event in CONTROL_EVENTS if event.lower() in lower]
        record.events = sorted(set(events + controls))
        if not record.events:
            primary = infer_primary_event(record.name, feature_text)
            record.events = [primary or "OTHER"]

        record.context_terms = sorted({term for term in CONTEXT_TERMS if term.lower() in lower})
        record.temporal_terms = sorted(
            {
                term
                for term in ["BEFORE", "AFTER", "order", "position", "exists", "for all", "implies"]
                if term.lower() in lower
            }
        )
        condition_hits = len(re.findall(r"\b(and|or|if|exists|for all|where|implies|not)\b|[<>]=?|=", lower))
        raw_complexity = len(record.context_terms) + len(record.temporal_terms) + condition_hits
        record.complexity = min(10, max(1, round(raw_complexity / 2)))

    event_counts = Counter(event for record in records for event in record.events)
    for record in records:
        record.coverage_score = round(sum(1 / event_counts[event] for event in record.events), 4)

    return event_counts


def heuristic_audit(records):
    groups = defaultdict(list)
    for record in records:
        family = rule_family(record.name)
        signature = (
            family,
            tuple(sorted(record.context_terms)),
            "FORBIDDEN" if "FORBIDDEN" in record.name else "REQUIRED" if "REQUIRED" in record.name else "",
        )
        groups[signature].append(record)

    for signature, grouped in groups.items():
        if len(grouped) > 1 and signature[0] in {"USER_RIGHT", "DATA_TRANSFER", "DATA_COLLECTION", "DATA_PROCESSING", "DATA_ACCESS"}:
            merge_name = f"MERGED_{signature[0]}_{stable_group_id(signature)}"
            origin_rules = [item.name for item in sorted(grouped, key=lambda rule: rule.name)]
            for index, record in enumerate(sorted(grouped, key=lambda item: item.name)):
                record.status = "FUSIONADA" if index else "MODIFICADA"
                record.merge_group = merge_name
                record.origin_rules = origin_rules
                record.finding = "Conditions overlap with related rules and can be represented as a parameterized OCL invariant."
                record.optimized_ocl = build_parameterized_rule(record, grouped, merge_name)
        else:
            for record in grouped:
                if record.complexity >= 18:
                    record.status = "MODIFICADA"
                    record.finding = "Rule is valid but has high logical density; split named subconditions or make sequencing explicit."
                    record.optimized_ocl = simplify_rule(record)
                else:
                    record.status = "CORRECTA"
                    record.finding = "Rule is syntactically consistent and aligned with the implemented validator."
                    record.optimized_ocl = record.ocl
                record.origin_rules = [record.name]

    suggested = suggest_new_rules(records)
    return {
        "engine": "heuristic",
        "summary": "Deterministic audit used because Phi-4-mini was disabled or unavailable.",
        "suggested_rules": suggested,
    }


def rule_family(rule_name):
    if rule_name.startswith("USER_RIGHT"):
        return "USER_RIGHT"
    if rule_name.startswith("DATA_TRANSFER"):
        return "DATA_TRANSFER"
    if rule_name.startswith("DATA_COLLECTION"):
        return "DATA_COLLECTION"
    if rule_name.startswith("DATA_PROCESSING"):
        return "DATA_PROCESSING"
    if rule_name.startswith("DATA_ACCESS"):
        return "DATA_ACCESS"
    if rule_name.startswith("DATA_DELETION"):
        return "DATA_DELETION"
    if rule_name.startswith("CASE_END"):
        return "CASE_END"
    if rule_name.startswith("CASE_START"):
        return "CASE_START"
    if rule_name.startswith("AUTOMATED_DECISION"):
        return "AUTOMATED_DECISION"
    return rule_name.split("_", 1)[0]


def stable_group_id(signature):
    digest = hashlib.sha1(repr(signature).encode("utf-8")).hexdigest()
    return digest[:8].upper()


def build_parameterized_rule(record, grouped, merge_name):
    names = ", ".join(item.name for item in sorted(grouped, key=lambda rule: rule.name))
    controls = sorted({event for item in grouped for event in item.events if event in CONTROL_EVENTS})
    controls_text = ", ".join(controls) if controls else "required_control"
    family = rule_family(record.name)
    return "\n".join(
        [
            "context Trace",
            f"inv {merge_name}:",
            f"    -- Refactors: {names}",
            f"    for all e where e.type belongs_to {family}:",
            f"        required controls {{{controls_text}}} satisfy configured BEFORE/AFTER ordering",
        ]
    )


def simplify_rule(record):
    return "\n".join(
        [
            record.ocl,
            "-- Optimization hint: extract context predicates and sequence predicates into named helper constraints.",
        ]
    )


def suggest_new_rules(records):
    names = {record.name for record in records}
    suggestions = []

    if "DATA_BREACH_NOTIFICATION_REQUIRED" not in names:
        suggestions.append(
            {
                "name": "DATA_BREACH_NOTIFICATION_REQUIRED",
                "reason": "No explicit rule covers GDPR Articles 33 and 34 breach notification timelines.",
                "ocl": "\n".join(
                    [
                        "context Trace",
                        "inv DATA_BREACH_NOTIFICATION_REQUIRED:",
                        "    for all e where e.name = detect_personal_data_breach:",
                        "        exists g where g.name = notify_supervisory_authority AND g.order > e.order",
                    ]
                ),
            }
        )

    if "CONSENT_WITHDRAWAL_STOP_PROCESSING" not in names:
        suggestions.append(
            {
                "name": "CONSENT_WITHDRAWAL_STOP_PROCESSING",
                "reason": "Consent withdrawal is not explicitly connected to halting subsequent processing.",
                "ocl": "\n".join(
                    [
                        "context Trace",
                        "inv CONSENT_WITHDRAWAL_STOP_PROCESSING:",
                        "    for all e where e.name = withdraw_consent:",
                        "        not exists p where p.type = DATA_PROCESSING AND p.order > e.order",
                    ]
                ),
            }
        )

    if "DPIA_HIGH_RISK_PROCESSING_REQUIRED" not in names:
        suggestions.append(
            {
                "name": "DPIA_HIGH_RISK_PROCESSING_REQUIRED",
                "reason": "High-risk or special-category processing should be linked to a DPIA evidence event.",
                "ocl": "\n".join(
                    [
                        "context Trace",
                        "inv DPIA_HIGH_RISK_PROCESSING_REQUIRED:",
                        "    if context.data_category in {SPECIAL, HEALTH}:",
                        "        exists g where g.name = perform_dpia AND g.order < first(DATA_PROCESSING).order",
                    ]
                ),
            }
        )

    return suggestions


def run_phi4_audit(records, model_id, max_new_tokens, backend):
    if backend == "none":
        return None

    prompt = build_phi4_prompt(records)
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype="auto",
            trust_remote_code=True,
        )
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        output = generator(prompt, max_new_tokens=max_new_tokens, do_sample=False)[0]["generated_text"]
        return parse_phi4_json(output)
    except Exception as exc:
        if backend == "transformers":
            raise
        return {
            "engine": "heuristic_after_phi4_unavailable",
            "summary": f"Phi-4-mini was unavailable, so deterministic audit was used. Reason: {exc}",
            "suggested_rules": [],
        }


def build_phi4_prompt(records):
    compact_rules = []
    for record in records[:45]:
        compact_rules.append(
            {
                "name": record.name,
                "events": record.events,
                "context_terms": record.context_terms,
                "ocl": truncate(record.ocl, 900),
            }
        )

    return (
        "You are auditing GDPR process-mining OCL rules. Return strict JSON with keys: "
        "rule_findings (list of {name,status,finding,merge_group,origin_rules,optimized_ocl}), "
        "suggested_rules (list of {name,reason,ocl}), summary. "
        "Allowed statuses: CORRECTA, MODIFICADA, FUSIONADA. Analyze redundancies, "
        "ambiguities, and missing GDPR coverage.\n\nRules:\n"
        + json.dumps(compact_rules, ensure_ascii=True)
    )


def parse_phi4_json(output):
    start = output.find("{")
    end = output.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(output[start : end + 1])
    except json.JSONDecodeError:
        return None


def apply_llm_findings(records, llm_result):
    if not llm_result or not llm_result.get("rule_findings"):
        return

    findings = {item.get("name", "").upper(): item for item in llm_result.get("rule_findings", [])}
    for record in records:
        item = findings.get(record.name)
        if not item:
            continue
        status = item.get("status", record.status).upper()
        if status in {"CORRECTA", "MODIFICADA", "FUSIONADA"}:
            record.status = status
        record.finding = item.get("finding") or record.finding
        record.merge_group = item.get("merge_group") or record.merge_group
        origin_rules = item.get("origin_rules")
        if isinstance(origin_rules, list) and origin_rules:
            record.origin_rules = [str(origin).upper() for origin in origin_rules]
        record.optimized_ocl = item.get("optimized_ocl") or record.optimized_ocl or record.ocl


def compute_metrics(records, suggested_rules):
    initial = len(records)
    merge_groups = {record.merge_group for record in records if record.merge_group}
    merged_members = sum(1 for record in records if record.status == "FUSIONADA")
    optimized = max(1, initial - merged_members + len(suggested_rules))
    compression_ratio = round((initial - optimized) / initial, 4) if initial else 0.0
    average_complexity = round(sum(record.complexity for record in records) / initial, 2) if initial else 0.0

    return {
        "initial_rules": initial,
        "optimized_rules": optimized,
        "suggested_rules": len(suggested_rules),
        "merge_groups": len(merge_groups),
        "compression_ratio": compression_ratio,
        "average_logic_complexity": average_complexity,
        "status_distribution": dict(Counter(record.status for record in records)),
    }


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_metrics_csv(path, records, metrics, event_counts):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            if key == "status_distribution":
                writer.writerow([key, json.dumps(value, ensure_ascii=False)])
            else:
                writer.writerow([key, value])
        writer.writerow([])
        writer.writerow(["event", "rule_count"])
        for event, count in event_counts.most_common():
            writer.writerow([event, count])
        writer.writerow([])
        writer.writerow(["rule", "status", "merge_group", "origin_rules", "complexity", "coverage_score", "events"])
        for record in sorted(records, key=lambda item: item.name):
            writer.writerow(
                [
                    record.name,
                    record.status,
                    record.merge_group,
                    " + ".join(record.origin_rules or [record.name]),
                    record.complexity,
                    record.coverage_score,
                    "; ".join(record.events),
                ]
            )


def generate_charts(records, event_counts, output_dir):
    sns.set_theme(style="whitegrid")

    events, counts = zip(*event_counts.most_common()) if event_counts else ([], [])
    plt.figure(figsize=(12, 6))
    sns.barplot(x=list(events), y=list(counts), color="#2f6f9f")
    plt.xticks(rotation=45, ha="right")
    plt.title("Number of Rules by GDPR Event or Control Event")
    plt.ylabel("Rules")
    plt.xlabel("Event")
    plt.tight_layout()
    plt.savefig(output_dir / "ocl_rules_by_event.png", dpi=180)
    plt.close()

    status_counts = Counter(record.status for record in records)
    plt.figure(figsize=(7, 5))
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors_map = {"CORRECTA": "#2ca25f", "MODIFICADA": "#f0ad4e", "FUSIONADA": "#3b82f6"}
    plt.pie(values, labels=labels, autopct="%1.1f%%", colors=[colors_map.get(label, "#888888") for label in labels])
    plt.title("Distribution of Valid, Modified, and Merged Rules")
    plt.tight_layout()
    plt.savefig(output_dir / "ocl_rule_status_distribution.png", dpi=180)
    plt.close()

    top_events = [event for event, _ in event_counts.most_common(18)]
    matrix = []
    rule_names = []
    for record in sorted(records, key=lambda item: item.name):
        rule_names.append(record.name)
        matrix.append([1 if event in record.events else 0 for event in top_events])

    if matrix and top_events:
        height = max(7, len(matrix) * 0.28)
        plt.figure(figsize=(12, height))
        sns.heatmap(matrix, cmap="Blues", cbar=False, xticklabels=top_events, yticklabels=rule_names, linewidths=0.2)
        plt.xticks(rotation=45, ha="right")
        plt.yticks(fontsize=7)
        plt.title("Rule/Event Coverage Overlap Matrix")
        plt.tight_layout()
        plt.savefig(output_dir / "ocl_rule_event_overlap_heatmap.png", dpi=180)
        plt.close()


def image_flowable(path, max_width, max_height):
    if not Path(path).exists():
        return Paragraph(f"Missing image: {path}", getSampleStyleSheet()["BodyText"])
    image = Image(str(path))
    ratio = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * ratio
    image.drawHeight = image.imageHeight * ratio
    return image


def paragraph(text, style):
    return Paragraph(html.escape(str(text)).replace("\n", "<br/>"), style)


def truncate(value, length=80):
    value = str(value).replace("\n", " ").strip()
    return value if len(value) <= length else value[: length - 3] + "..."


def fusion_trace(record):
    origins = record.origin_rules or [record.name]
    if record.merge_group:
        return f"{record.merge_group} (Fusiona: {' + '.join(origins)})"
    if record.status == "FUSIONADA":
        return f"Fusiona: {' + '.join(origins)}"
    return "-"


def wrap_ocl_code(code, width=96):
    wrapped_lines = []
    for line in code.splitlines():
        if len(line) <= width:
            wrapped_lines.append(line)
            continue
        indent = re.match(r"\s*", line).group(0)
        chunks = textwrap.wrap(
            line.strip(),
            width=max(30, width - len(indent)),
            subsequent_indent=indent + "    ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        if chunks:
            wrapped_lines.append(indent + chunks[0])
            wrapped_lines.extend(chunks[1:])
        else:
            wrapped_lines.append(line)
    return "\n".join(wrapped_lines)


def ocl_code_card(title, code, styles):
    title_row = [paragraph(title, styles["CodeTitle"])]
    code_row = [Preformatted(wrap_ocl_code(code), styles["CodeSmall"])]
    table = Table([title_row, code_row], colWidths=[18 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#cbd5e1")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def optimized_rule_cards(records, suggested_rules):
    cards = []
    emitted_groups = set()
    for record in sorted(records, key=lambda item: item.name):
        if record.merge_group:
            if record.merge_group in emitted_groups:
                continue
            emitted_groups.add(record.merge_group)
            title = f"[FUSIONADA] {record.merge_group} (Fusiona: {' + '.join(record.origin_rules or [record.name])})"
        else:
            title = f"[{record.status}] {record.name}"
        cards.append((title, record.optimized_ocl or record.ocl))

    for item in suggested_rules:
        cards.append((f"[SUGERIDA] {item['name']}", item["ocl"]))

    return cards


def build_pdf(records, metrics, event_counts, suggested_rules, llm_summary, output_dir, report_path):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCenter",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=19,
            leading=23,
            spaceAfter=16,
        )
    )
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.1,
            leading=8.2,
            textColor=colors.white,
        )
    )
    styles.add(ParagraphStyle(name="CodeSmall", parent=styles["Code"], fontName="Courier", fontSize=7.2, leading=8.4))
    styles.add(ParagraphStyle(name="CodeTitle", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=13, leading=16, spaceBefore=12))

    doc = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.1 * cm,
        bottomMargin=1.1 * cm,
    )
    story = []

    story.append(Paragraph("OCL Rules Optimization and Formal Audit", styles["TitleCenter"]))
    story.append(Paragraph(f"Execution date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["BodyText"]))
    story.append(
        Paragraph(
            "Objective: audit the GDPR OCL rule set used by the deterministic validator, identify redundant or ambiguous constraints, quantify coverage, and produce an optimized OCL appendix.",
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 0.25 * cm))
    story.append(
        paragraph(
            llm_summary.get("summary", "Audit completed.") if isinstance(llm_summary, dict) else "Audit completed.",
            styles["Small"],
        )
    )

    story.append(Paragraph("1. Catalog of Validated and Optimized Rules", styles["Section"]))
    table_data = [[
        paragraph("Rule", styles["TableHeader"]),
        paragraph("Status", styles["TableHeader"]),
        paragraph("Fusion Trace", styles["TableHeader"]),
        paragraph("Events", styles["TableHeader"]),
        paragraph("Complexity\n(1-10)", styles["TableHeader"]),
        paragraph("Finding", styles["TableHeader"]),
    ]]
    for record in sorted(records, key=lambda item: item.name):
        table_data.append(
            [
                paragraph(record.name, styles["Small"]),
                paragraph(f"[{record.status}]", styles["Small"]),
                paragraph(truncate(fusion_trace(record), 95), styles["Small"]),
                paragraph(truncate(", ".join(record.events), 55), styles["Small"]),
                str(record.complexity),
                paragraph(truncate(record.finding, 120), styles["Small"]),
            ]
        )
    table = Table(table_data, colWidths=[3.05 * cm, 1.7 * cm, 4.45 * cm, 3.0 * cm, 1.75 * cm, 4.05 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 6.6),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    story.append(table)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("New Rules Suggested", styles["Heading3"]))
    for item in suggested_rules:
        story.append(KeepTogether([paragraph(f"{item['name']}: {item['reason']}", styles["Small"]), Spacer(1, 0.08 * cm)]))

    story.append(PageBreak())
    story.append(Paragraph("2. Statistical Experiment and Coverage Metrics", styles["Section"]))
    metrics_rows = [["Metric", "Value"]]
    for key, value in metrics.items():
        if key != "status_distribution":
            metrics_rows.append([key.replace("_", " ").title(), str(value)])
    metrics_rows.append(["Status Distribution", json.dumps(metrics["status_distribution"], ensure_ascii=False)])
    metrics_table = Table(metrics_rows, colWidths=[7 * cm, 9 * cm])
    metrics_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(metrics_table)
    story.append(Spacer(1, 0.18 * cm))
    story.append(
        paragraph(
            "Complexity is a normalized 1-10 score calculated from each rule's logical structure: context predicates, temporal/position checks, existence clauses, boolean operators, and relational comparisons. A value of 1 represents a simple single-attribute or single-event condition; 10 represents a dense rule with multiple context checks and sequence constraints. The raw condition count is normalized and capped at 10 to keep the metric comparable across rules.",
            styles["Small"],
        )
    )
    story.append(Spacer(1, 0.25 * cm))
    story.append(image_flowable(output_dir / "ocl_rules_by_event.png", 18 * cm, 8.2 * cm))
    story.append(Spacer(1, 0.25 * cm))
    story.append(image_flowable(output_dir / "ocl_rule_status_distribution.png", 18 * cm, 8.2 * cm))
    story.append(Spacer(1, 0.25 * cm))
    story.append(image_flowable(output_dir / "ocl_rule_event_overlap_heatmap.png", 18 * cm, 14 * cm))

    story.append(PageBreak())
    story.append(Paragraph("3. Refactored OCL Code Appendix", styles["Section"]))
    story.append(
        paragraph(
            "Each block below is rendered as an independent optimized invariant. Merged blocks explicitly state the original rules that feed the refactoring.",
            styles["Small"],
        )
    )
    story.append(Spacer(1, 0.2 * cm))

    for title, code in optimized_rule_cards(records, suggested_rules):
        card = ocl_code_card(title, code, styles)
        if len(code) < 1600:
            story.append(KeepTogether([card, Spacer(1, 0.18 * cm)]))
        else:
            story.append(card)
            story.append(Spacer(1, 0.18 * cm))

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)


def split_code_blocks(text, max_chars=3400):
    blocks = text.split("\n\n")
    chunks = []
    current = []
    current_len = 0
    for block in blocks:
        block_len = len(block) + 2
        if current and current_len + block_len > max_chars:
            chunks.append("\n\n".join(current))
            current = [block]
            current_len = block_len
        else:
            current.append(block)
            current_len += block_len
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(1.2 * cm, 0.6 * cm, "GDPR Trace - OCL Rules Audit")
    canvas.drawRightString(A4[0] - 1.2 * cm, 0.6 * cm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / REPORT_PATH.name

    source_text, source_path = read_rule_source()
    primary_records = extract_ocl_rules_from_text(source_text, source_path)
    fallback_records = extract_rules_from_validator()
    records = merge_sources(primary_records, fallback_records)

    if not records:
        raise RuntimeError("No OCL or validator rules could be extracted.")

    event_counts = enrich_rule_features(records)
    heuristic_summary = heuristic_audit(records)
    llm_result = run_phi4_audit(records, args.model_id, args.max_new_tokens, args.backend)
    if llm_result and llm_result.get("rule_findings"):
        apply_llm_findings(records, llm_result)
        suggested_rules = llm_result.get("suggested_rules") or heuristic_summary["suggested_rules"]
    else:
        if llm_result and llm_result.get("summary"):
            heuristic_summary["summary"] = llm_result["summary"]
            heuristic_summary["engine"] = llm_result.get("engine", heuristic_summary["engine"])
        suggested_rules = heuristic_summary["suggested_rules"]

    metrics = compute_metrics(records, suggested_rules)
    event_counts = enrich_rule_features(records)

    generate_charts(records, event_counts, output_dir)
    write_metrics_csv(output_dir / "ocl_rule_metrics.csv", records, metrics, event_counts)
    write_json(
        output_dir / "ocl_rules_audit.json",
        {
            "source": source_path,
            "model_backend": args.backend,
            "model_id": args.model_id,
            "llm_summary": heuristic_summary if not llm_result else llm_result,
            "metrics": metrics,
            "rules": [asdict(record) for record in records],
            "suggested_rules": suggested_rules,
        },
    )
    build_pdf(records, metrics, event_counts, suggested_rules, heuristic_summary if not llm_result else llm_result, output_dir, report_path)

    print(f"Extracted rules: {len(records)}")
    print(f"Compression ratio: {metrics['compression_ratio']}")
    print(f"Audit JSON: {output_dir / 'ocl_rules_audit.json'}")
    print(f"Metrics CSV: {output_dir / 'ocl_rule_metrics.csv'}")
    print(f"PDF report: {report_path}")


if __name__ == "__main__":
    main()
