# gdpr/scoring.py

SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 3,
    "high": 5
}

RISK_LEVEL_MULTIPLIER = {
    "procedural": 1,
    "critical": 2
}


def compute_gdpr_risk_score(recommendations):
    """
    Calcula un score GDPR (0–100) a partir de las recomendaciones.
    """
    raw_score = 0

    for rec in recommendations:
        severity = rec.get("severity", "low")
        risk_level = rec.get("risk_level", "procedural")

        severity_weight = SEVERITY_WEIGHTS.get(severity, 1)
        risk_multiplier = RISK_LEVEL_MULTIPLIER.get(risk_level, 1)

        raw_score += severity_weight * risk_multiplier

    # Normalización simple (ajustable)
    score = min(100, raw_score * 5)

    return score


def classify_risk(score):
    if score == 0:
        return "none"
    elif score < 30:
        return "low"
    elif score < 70:
        return "medium"
    else:
        return "high"
