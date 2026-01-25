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
