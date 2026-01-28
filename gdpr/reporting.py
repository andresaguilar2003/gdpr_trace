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

    VIOLATION_LABELS = {
        "data_minimization_violation": "Data minimization violation",
        "purpose_violation": "Purpose limitation violation",
        "access_without_consent": "Access without valid consent",
        "access_after_consent_expiration": "Access after consent expiration",
        "missing_right_response": "Failure to respond to data subject rights",
        "access_after_erasure": "Access after data erasure",
        "implicit_consent": "Implicit consent used",
        "missing_access_log": "Missing access logging",
        "sp_access_after_consent_expiration": "Sticky Policy: access after consent expiration"
    }

    violations = []
    risk_levels = []

    # ==================================================
    # COLLECT DATA
    # ==================================================
    for trace in trace_records:
        risk_levels.append(trace.get("risk_level", "none"))
        violations.extend(trace.get("violations", []))

    # ==================================================
    # GROUP VIOLATIONS BY TYPE
    # ==================================================
    violations_by_type = {}
    for v in violations:
        v_type = v["type"]
        violations_by_type.setdefault(v_type, []).append(v)

    violations_summary = []
    recommendations_by_type = {}

    for v_type, items in violations_by_type.items():
        first_violation = items[0]
        first_event = (
            first_violation["events"][0]
            if first_violation.get("events")
            else None
        )

        # -------------------------
        # VIOLATION SUMMARY
        # -------------------------
        priority_map = {
            "high": "Immediate action required",
            "medium": "Corrective action recommended",
            "low": "Monitor and improve"
        }

        violations_summary.append({
            "violation": v_type,  # ID técnico
            "display_name": VIOLATION_LABELS.get(
                v_type,
                v_type.replace("_", " ").capitalize()
            ),
            "severity": first_violation.get("severity"),
            "priority": priority_map.get(
                first_violation.get("severity"), "Review required"
            ),
            "legal_reference": first_violation.get("legal_reference"),
            "occurrences": len(items),
            "example_event": {
                "timestamp": first_event.get("time:timestamp") if first_event else None,
                "activity": first_event.get("concept:name") if first_event else None
            }
        })




        # -------------------------
        # ONE RECOMMENDATION PER TYPE
        # -------------------------
        for trace in trace_records:
            for r in trace.get("recommendations", []):
                if r.get("violation") == v_type:
                    recommendations_by_type[v_type] = r
                    break
            if v_type in recommendations_by_type:
                break

    # ==================================================
    # OVERALL RISK
    # ==================================================
    overall_risk = max(
        risk_levels,
        key=lambda r: ["none", "low", "medium", "high"].index(r)
    )

    executive_message = {
        "none": "No significant GDPR compliance issues were detected.",
        "low": "Minor GDPR compliance gaps were identified. Improvements are recommended.",
        "medium": "Several GDPR compliance issues were detected. Corrective actions are advised.",
        "high": (
            "Critical GDPR compliance risks were identified. "
            "Immediate corrective actions are strongly recommended."
        )
    }[overall_risk]

    # ==================================================
    # FINAL REPORT
    # ==================================================
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
        "recommendations": list(recommendations_by_type.values()),
        "conclusion": {
            "summary": (
                "This report provides an executive assessment of GDPR compliance "
                "based on the analysis of operational process execution logs."
            ),
            "recommended_next_steps": [
                "Immediately address critical GDPR violations",
                "Review consent and access governance mechanisms",
                "Introduce continuous GDPR compliance monitoring"
            ]
        }
    }
