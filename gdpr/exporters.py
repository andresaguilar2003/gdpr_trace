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

import shutil


def export_markdown_report(report, output_dir, filename, severity_chart_path=None):
    import os

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    meta = report["metadata"]
    summary = report["executive_summary"]

    lines = []

    # ==================================================
    # YAML METADATA (REAL COVER PAGE FOR PANDOC)
    # ==================================================
    lines.append("---")
    lines.append("title: GDPR Compliance Analysis Report")
    lines.append("subtitle: Executive Compliance Assessment")
    lines.append(f"date: {meta['analysis_date']}")
    lines.append("documentclass: report")
    lines.append("fontsize: 11pt")
    lines.append("geometry: margin=2.5cm")
    lines.append("---\n")

    # Force cover page
    lines.append("\\newpage\n")

    # ==================================================
    # EXECUTIVE OVERVIEW (FIRST CONTENT PAGE)
    # ==================================================
    lines.append("# Executive Overview\n")
    lines.append(f"**Input system log:** {meta['input_log']}")
    lines.append(f"**Total traces analyzed:** {meta['total_traces_analyzed']}\n")

    lines.append(
        f"**Overall GDPR Risk Level:** "
        f"**{summary['overall_risk_level'].upper()}**\n"
    )

    lines.append(
        f"- Total GDPR violations detected: "
        f"**{summary['total_violations']}**"
    )
    lines.append(
        f"- Critical violations: "
        f"**{summary['critical_violations']}**\n"
    )

    lines.append("\\newpage\n")

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================
    lines.append("# Executive Summary\n")
    if summary.get("executive_message"):
        lines.append(summary["executive_message"] + "\n")

        # ==================================================
        # EXECUTIVE RISK TABLE
        # ==================================================
        lines.append("# GDPR Risk Overview\n")
        lines.append("| Violation type | Severity | Occurrences | Action priority |")
        lines.append("|---------------|----------|-------------|-----------------|")

        for v in report.get("violations_summary", []):
            lines.append(
                f"| {v['display_name']} | "
                f"{v['severity']} | "
                f"{v['occurrences']} | "
                f"{v.get('priority', '')} |"
            )

        lines.append("\n\\newpage\n")

    # ==================================================
    # EXECUTIVE RISK TABLE
    # ==================================================
    lines.append("# GDPR Risk Overview\n")
    lines.append("| Violation type | Severity | Occurrences | Action priority |")
    lines.append("|---------------|----------|-------------|-----------------|")

    for v in report.get("violations_summary", []):
        lines.append(
            f"| {v['display_name']} | "
            f"{v['severity']} | "
            f"{v['occurrences']} | "
            f"{v.get('priority', '')} |"
        )

    lines.append("\n\\newpage\n")

    # ==================================================
    # SEVERITY OVERVIEW CHART
    # ==================================================
    if severity_chart_path:
        lines.append("# GDPR Violations Severity Overview\n")

        image_name = os.path.basename(severity_chart_path)
        target_image_path = os.path.join(output_dir, image_name)

        # Copy image next to markdown so Pandoc can find it
        if os.path.abspath(severity_chart_path) != os.path.abspath(target_image_path):
            shutil.copy(severity_chart_path, target_image_path)

        lines.append(f"![GDPR violations by severity]({image_name})\n")

        lines.append(
            "This chart provides an aggregated view of GDPR violations "
            "classified by severity level.\n"
        )
        lines.append("\\newpage\n")




    # ==================================================
    # KEY COMPLIANCE SIGNALS
    # ==================================================
    lines.append("# Key Compliance Signals\n")

    signals = []

    if summary["overall_risk_level"] == "high":
        signals.append("CRITICAL GDPR risk detected across multiple process executions.")

    if summary["critical_violations"] > 0:
        signals.append(
            "Repeated high-severity violations indicate structural compliance gaps."
        )

    if summary["total_violations"] > len(report.get("violations_summary", [])) * 5:
        signals.append(
            "Violations are recurrent, suggesting systematic process issues."
        )

    if not signals:
        signals.append("No critical GDPR compliance signals detected.")

    for s in signals:
        lines.append(f"- {s}")

    lines.append("\n\\newpage\n")


    # ==================================================
    # VIOLATIONS SUMMARY
    # ==================================================
    lines.append("# Identified GDPR Violations\n")

    for v in report.get("violations_summary", []):
        lines.append(f"## {v['display_name']}")
        lines.append(f"- **Severity:** {v['severity']}")
        lines.append(f"- **Legal reference:** {v.get('legal_reference')}")
        lines.append(f"- **Occurrences:** {v['occurrences']}")

        ex = v.get("example_event")
        if ex and ex.get("activity"):
            lines.append(
                f"- **Example event:** `{ex['activity']}` "
                f"({ex['timestamp']})"
            )
        lines.append("")

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================
    lines.append("# Priority Recommendations\n")

    for r in report.get("recommendations", []):
        lines.append(f"## Recommendation: {r.get('title')}")
        lines.append(f"- **Risk level:** {r.get('risk_level')}")
        lines.append(f"- **Legal reference:** {r.get('legal_reference')}")
        lines.append(f"- **Recommendation:** {r.get('recommendation')}\n")

    # ==================================================
    # CONCLUSION
    # ==================================================
    conclusion = report.get("conclusion", {})
    if conclusion:
        lines.append("# Conclusion\n")
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

def _safe_rmtree(path):
    import shutil
    import os
    import stat

    def onerror(func, path, exc_info):
        # Try to fix permission issues on Windows
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass  # If it still fails, ignore safely

    shutil.rmtree(path, onerror=onerror)


def export_pdf_report(md_path, cleanup_images=True):
    import subprocess
    import shutil
    import os
    import glob

    if not shutil.which("pandoc"):
        raise RuntimeError("Pandoc is not installed or not available in PATH.")

    output_dir = os.path.dirname(md_path)
    pdf_path = md_path.replace(".md", ".pdf")

    subprocess.run(
        [
            "pandoc",
            os.path.basename(md_path),
            "-o", os.path.basename(pdf_path),
            "--pdf-engine=xelatex",
            "--toc",
            "--toc-depth=2",
            "-V", "geometry:margin=2.5cm"
        ],
        cwd=output_dir,
        check=True
    )

    # 🧹 Remove temporary images
    if cleanup_images:
        for img in glob.glob(os.path.join(output_dir, "*.png")):
            if "gdpr_severity" in img:
                try:
                    os.remove(img)
                except PermissionError:
                    pass

    # 🧹 Remove pandoc media folders (Windows-safe)
    for item in os.listdir(output_dir):
        if item.startswith("media-"):
            media_path = os.path.join(output_dir, item)
            if os.path.isdir(media_path):
                try:
                    _safe_rmtree(media_path)
                except Exception:
                    pass

    return pdf_path
