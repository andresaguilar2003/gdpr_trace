from collections import Counter

def build_trace_ranking(all_recommendations):
    """
    Genera un ranking de trazas según riesgo GDPR,
    diferenciando violaciones técnicas y Sticky Policies.
    """

    ranking = []

    for trace in all_recommendations:
        recs = trace.get("recommendations", [])

        violations = [r for r in recs if "violation" in r]
        sp_alerts = [r for r in recs if r.get("type", "").startswith("sp_")]

        violation_types = [
            r["violation"] for r in recs if "violation" in r
        ]
        top_violation = None

        if violation_types:
            top_violation = Counter(violation_types).most_common(1)[0][0]

        ranking.append({
            "trace_id": trace.get("trace_id"),
            "risk_score": trace.get("risk_score", 0),
            "risk_level": trace.get("risk_level", "none"),
            "num_violations": len(violations),
            "num_sticky_policy_alerts": len(sp_alerts),
            "top_violation": top_violation
        })

    ranking.sort(key=lambda x: x["risk_score"], reverse=True)
    return ranking

