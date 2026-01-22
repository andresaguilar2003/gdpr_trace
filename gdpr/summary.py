# gdpr/summary.py

from collections import Counter
from statistics import mean


def summarize_recommendations(all_recommendations, top_n=5):
    """
    Genera un resumen global de cumplimiento GDPR a partir
    de las recomendaciones y scores calculados por traza.

    IMPORTANTE:
    - Distingue entre violaciones técnicas y alertas de Sticky Policy (SP)
    """

    total_traces = len(all_recommendations)
    traces_with_violations = 0

    # -----------------------------
    # Contadores globales
    # -----------------------------
    violation_counter = Counter()     # Violaciones técnicas
    severity_counter = Counter()
    risk_level_counter = Counter()
    sp_counter = Counter()            # Sticky Policy alerts

    # -----------------------------
    # Métricas agregadas
    # -----------------------------
    violations_per_trace = []
    risk_scores = []

    for trace_rec in all_recommendations:
        recs = trace_rec.get("recommendations", [])
        trace_risk_score = trace_rec.get("risk_score", 0)
        trace_risk_level = trace_rec.get("risk_level", "none")

        # -----------------------------
        # Separar tipos de recomendaciones
        # -----------------------------
        technical_violations = [
            r for r in recs if "violation" in r
        ]

        sp_alerts = [
            r for r in recs if r.get("type", "").startswith("sp_")
        ]

        # Conteo por traza (SOLO violaciones técnicas)
        if technical_violations:
            traces_with_violations += 1
            violations_per_trace.append(len(technical_violations))

        # Contabilizar violaciones técnicas
        for rec in technical_violations:
            violation_counter[rec["violation"]] += 1
            severity_counter[rec.get("severity", "unknown")] += 1

        # Contabilizar Sticky Policies
        for rec in sp_alerts:
            sp_counter[rec["type"]] += 1

        # Risk score (YA calculado en scoring.py)
        risk_scores.append(trace_risk_score)
        risk_level_counter[trace_risk_level] += 1

    # -----------------------------
    # Métricas agregadas
    # -----------------------------
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
        # ANÁLISIS DE VIOLACIONES TÉCNICAS
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
        # GDPR RISK SCORING
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
        # STICKY POLICY ANALYSIS (GOVERNANCE)
        # --------------------------------------------------
        "sticky_policy_analysis": {
            "total_sp_alerts": sum(sp_counter.values()),
            "top_sp_alerts": sp_counter.most_common(top_n)
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
                "and breach notification deadlines. Sticky Policy alerts indicate "
                "structural or governance-level risks that may require "
                "organizational actions beyond process remediation."
            )
        }
    }

    return summary
