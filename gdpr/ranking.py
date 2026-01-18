from collections import Counter


def build_trace_ranking(all_recommendations):
    """
    Genera un ranking de trazas según riesgo GDPR.
    """

    ranking = []

    for trace in all_recommendations:
        recs = trace.get("recommendations", [])

        violation_types = [r["violation"] for r in recs]
        top_violation = None

        if violation_types:
            top_violation = Counter(violation_types).most_common(1)[0][0]

        ranking.append({
            "trace_id": trace.get("trace_id"),
            "risk_score": trace.get("risk_score", 0),
            "risk_level": trace.get("risk_level", "none"),
            "num_violations": len(recs),
            "top_violation": top_violation
        })

    # Ordenar de mayor a menor riesgo
    ranking.sort(key=lambda x: x["risk_score"], reverse=True)

    return ranking
