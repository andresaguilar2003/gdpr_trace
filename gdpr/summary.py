# gdpr/summary.py

from collections import Counter
from statistics import mean


def summarize_recommendations(all_recommendations, top_n=5):
    """
    Genera un resumen global de cumplimiento GDPR a partir
    de las recomendaciones y scores calculados por traza.
    """

    total_traces = len(all_recommendations)
    traces_with_violations = 0

    # Contadores globales
    violation_counter = Counter()
    severity_counter = Counter()
    risk_level_counter = Counter()

    # Métricas agregadas
    violations_per_trace = []
    risk_scores = []

    for trace_rec in all_recommendations:
        recs = trace_rec.get("recommendations", [])
        trace_risk_score = trace_rec.get("risk_score", 0)
        trace_risk_level = trace_rec.get("risk_level", "none")

        # Conteo por traza
        if recs:
            traces_with_violations += 1
            violations_per_trace.append(len(recs))

        # Contabilizar recomendaciones
        for rec in recs:
            violation_counter[rec.get("violation", "unknown")] += 1
            severity_counter[rec.get("severity", "unknown")] += 1

        # Risk score (YA calculado en scoring.py)
        risk_scores.append(trace_risk_score)
        risk_level_counter[trace_risk_level] += 1

    # Métricas agregadas
    avg_violations = mean(violations_per_trace) if violations_per_trace else 0
    avg_risk_score = mean(risk_scores) if risk_scores else 0
    max_risk_score = max(risk_scores) if risk_scores else 0

    summary = {
        # --------------------------------------------------
        # VISIÓN GENERAL
        # --------------------------------------------------
        "overview": {
            "total_traces_analyzed": total_traces,
            "traces_with_violations": traces_with_violations,
            "percentage_non_compliant": round(
                (traces_with_violations / total_traces) * 100, 2
            ) if total_traces else 0
        },

        # --------------------------------------------------
        # ANÁLISIS DE VIOLACIONES
        # --------------------------------------------------
        "violations_analysis": {
            "total_violations": sum(violation_counter.values()),
            "average_violations_per_trace": round(avg_violations, 2),
            "top_violations": violation_counter.most_common(top_n)
        },

        # --------------------------------------------------
        # ANÁLISIS DE SEVERIDAD
        # --------------------------------------------------
        "severity_analysis": {
            "severity_distribution": dict(severity_counter)
        },

        # --------------------------------------------------
        # GDPR RISK SCORING (OFICIAL)
        # --------------------------------------------------
        "gdpr_risk_scoring": {
            "average_risk_score": round(avg_risk_score, 2),
            "max_risk_score": max_risk_score,
            "risk_level_distribution": dict(risk_level_counter),
            "risk_scale": {
                "0": "none",
                "1–29": "low",
                "30–69": "medium",
                "70–100": "high"
            }
        },

        # --------------------------------------------------
        # INTERPRETACIÓN AUTOMÁTICA
        # --------------------------------------------------
        "interpretation": {
            "main_risks": [
                v for v, _ in violation_counter.most_common(3)
            ],
            "priority_action": (
                "Prioritize mitigation of high and medium GDPR risk traces, "
                "focusing especially on consent management, restriction periods "
                "and breach notification deadlines."
            )
        }
    }

    return summary
