# gdpr/exporters.py

import os
import json
from datetime import datetime


def export_recommendations(data, output_dir, filename="recommendations.json"):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    clean_data = sanitize(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    return path


# ============================================================
# SERIALIZACIÓN GENÉRICA
# ============================================================

def serialize_event(event):
    """
    Convierte un evento pm4py en un dict JSON-serializable.
    """
    serialized = {}

    for k, v in event.items():
        serialized[k] = sanitize(v)

    return serialized


def sanitize(obj):
    """
    Limpia recursivamente cualquier estructura para JSON.
    """

    # datetime → ISO
    if isinstance(obj, datetime):
        return obj.isoformat()

    # pm4py Event (dict-like)
    if hasattr(obj, "items") and obj.__class__.__name__ == "Event":
        return serialize_event(obj)

    # dict
    if isinstance(obj, dict):
        return {
            k: sanitize(v)
            for k, v in obj.items()
        }

    # list / tuple / set
    if isinstance(obj, (list, tuple, set)):
        return [sanitize(v) for v in obj]

    # tipos básicos
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # fallback defensivo (por si aparece algo raro)
    return str(obj)

def export_markdown_report(report, output_dir, filename):
    import os

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    lines = []

    meta = report["metadata"]
    summary = report["executive_summary"]

    # ==================================================
    # COVER PAGE
    # ==================================================
    lines.append("# GDPR Compliance Analysis Report\n")
    lines.append("---\n")
    lines.append("### Executive Compliance Assessment\n")
    lines.append(f"**Input system log:** {meta['input_log']}")
    lines.append(f"**Analysis date:** {meta['analysis_date']}")
    lines.append(f"**Total traces analyzed:** {meta['total_traces_analyzed']}\n")
    lines.append("---\n")
    lines.append("\\newpage\n")

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================
    risk_icon = {
        "none": "🟢",
        "low": "🟡",
        "medium": "🟠",
        "high": "🔴"
    }.get(summary["overall_risk_level"], "⚪")

    lines.append("## 1. Executive Summary\n")
    lines.append(
        f"**Overall GDPR Risk Level:** {risk_icon} "
        f"**{summary['overall_risk_level'].upper()}**\n"
    )
    lines.append(summary.get("executive_message", "") + "\n")

    lines.append("**Key figures:**")
    lines.append(f"- Total GDPR violations detected: **{summary['total_violations']}**")
    lines.append(f"- Critical violations: **{summary['critical_violations']}**\n")

    # ==================================================
    # VIOLATIONS SUMMARY
    # ==================================================
    lines.append("## 2. Main GDPR Findings\n")

    for v in report.get("violations_summary", []):
        lines.append(f"### ❌ {v['violation']}")
        lines.append(f"- Severity: **{v['severity']}**")
        lines.append(f"- Legal reference: {v.get('legal_reference')}")
        lines.append(f"- Occurrences: {v['occurrences']}")

        ex = v.get("example_event")
        if ex and ex.get("activity"):
            lines.append(
                f"- Example event: `{ex['activity']}` "
                f"({ex['timestamp']})"
            )
        lines.append("")

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================
    lines.append("## 3. Priority Recommendations\n")

    for r in report.get("recommendations", []):
        lines.append(f"### ✔ {r.get('title')}")
        lines.append(f"- Risk level: {r.get('risk_level')}")
        lines.append(f"- Legal reference: {r.get('legal_reference')}")
        lines.append(f"- Recommendation: {r.get('recommendation')}\n")

    # ==================================================
    # CONCLUSION
    # ==================================================
    conclusion = report.get("conclusion", {})
    lines.append("## 4. Conclusion\n")
    lines.append(conclusion.get("summary", ""))

    if "recommended_next_steps" in conclusion:
        lines.append("\n**Recommended next steps:**")
        for step in conclusion["recommended_next_steps"]:
            lines.append(f"- {step}")

    # ==================================================
    # WRITE FILE
    # ==================================================
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path



def export_pdf_report(md_path):
    import subprocess
    import shutil

    if not shutil.which("pandoc"):
        raise RuntimeError("Pandoc is not installed or not available in PATH.")

    pdf_path = md_path.replace(".md", ".pdf")

    subprocess.run([
        "pandoc",
        md_path,
        "-o", pdf_path,
        "--pdf-engine=xelatex",
        "--toc",
        "--toc-depth=2",
        "-V", "geometry:margin=2.5cm"
    ], check=True)

    return pdf_path
