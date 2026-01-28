from datetime import datetime
from gdpr.summary import summarize_recommendations
from gdpr.ranking import build_trace_ranking
from gdpr.audit import generate_audit_report
from gdpr.exporters import sanitize


def build_gdpr_analysis_report(all_recommendations, input_log_name):
    """
    Construye el informe completo de análisis GDPR listo para serialización JSON.
    """

    # Sanitizamos las trazas (violaciones, eventos, etc.)
    sanitized_traces = sanitize(all_recommendations)

    return {
        "metadata": {
            "input_log": input_log_name,
            "total_traces": len(all_recommendations),
            "analysis_timestamp": datetime.utcnow().isoformat()
        },
        "global_summary": summarize_recommendations(all_recommendations),
        "trace_ranking": build_trace_ranking(all_recommendations),
        "traces": [
            {
                **trace,
                "audit_report": generate_audit_report(trace)
            }
            for trace in sanitized_traces
        ]
    }


def build_gdpr_executive_report(trace_records, input_log_name):
    from datetime import datetime

    violations = []
    recommendations = []
    risk_levels = []

    for trace in trace_records:
        risk_levels.append(trace.get("risk_level", "none"))
        violations.extend(trace.get("violations", []))
        recommendations.extend(trace.get("recommendations", []))

    # Agrupar violaciones
    violations_by_type = {}
    for v in violations:
        v_type = v["type"]
        violations_by_type.setdefault(v_type, []).append(v)

    violations_summary = []
    for v_type, items in violations_by_type.items():
        first_event = items[0]["events"][0] if items[0].get("events") else None

        violations_summary.append({
            "violation": v_type,
            "severity": items[0].get("severity"),
            "legal_reference": items[0].get("legal_reference"),
            "occurrences": len(items),
            "example_event": {
                "timestamp": first_event.get("time:timestamp") if first_event else None,
                "activity": first_event.get("concept:name") if first_event else None
            }
        })

    overall_risk = max(
        risk_levels,
        key=lambda r: ["none", "low", "medium", "high"].index(r)
    )

    # 🧠 Texto ejecutivo según riesgo
    executive_message = {
        "none": "No significant GDPR compliance issues were detected.",
        "low": "Minor GDPR compliance gaps were identified. Improvements are recommended.",
        "medium": "Several GDPR compliance issues were detected. Corrective actions are advised.",
        "high": (
            "Critical GDPR compliance risks were identified. "
            "Immediate corrective actions are strongly recommended."
        )
    }[overall_risk]

    return {
        "metadata": {
            "input_log": input_log_name,
            "analysis_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_traces_analyzed": len(trace_records)
        },
        "executive_summary": {
            "overall_risk_level": overall_risk,
            "executive_message": executive_message,
            "total_violations": len(violations),
            "critical_violations": sum(
                1 for v in violations if v.get("severity") == "high"
            )
        },
        "violations_summary": violations_summary,
        "recommendations": recommendations,
        "conclusion": {
            "summary": (
                "This analysis highlights the current GDPR compliance posture "
                "based on observed process execution logs."
            ),
            "recommended_next_steps": [
                "Address critical GDPR violations immediately",
                "Review consent and access control mechanisms",
                "Implement continuous GDPR monitoring"
            ]
        }
    }
