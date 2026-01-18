def generate_audit_report(trace_record):
    """
    Genera un informe de auditoría GDPR por traza.
    """

    findings = []

    for rec in trace_record.get("recommendations", []):
        findings.append({
            "violation": rec.get("violation"),
            "severity": rec.get("severity"),
            "risk_level": rec.get("risk_level"),
            "legal_reference": rec.get("legal_reference"),
            "evidence": rec.get("recommendation"),
            "recommended_action": rec.get("title")
        })

    risk_level = trace_record.get("risk_level", "none")

    assessment_map = {
        "none": "No GDPR issues detected.",
        "low": "Low GDPR risk. Minor improvements recommended.",
        "medium": "Moderate GDPR risk. Corrective actions advised.",
        "high": "High GDPR risk. Immediate corrective actions required."
    }

    return {
        "trace_id": trace_record.get("trace_id"),
        "risk_score": trace_record.get("risk_score"),
        "risk_level": risk_level,
        "audit_findings": findings,
        "overall_assessment": assessment_map.get(risk_level, "")
    }
