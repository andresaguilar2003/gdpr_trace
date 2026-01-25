def generate_audit_report(trace_record):
    """
    Genera un informe de auditoría GDPR por traza.
    """

    findings = []

    # 🔴 Violaciones GDPR reales
    for v in trace_record.get("violations", []):
        findings.append({
            "type": "gdpr_violation",
            "violation": v.get("type"),
            "severity": v.get("severity"),
            "legal_reference": v.get("legal_reference"),
            "message": v.get("message"),
            "num_events": len(v.get("events", []))
        })

    # 🟡 Sticky Policy alerts (gobernanza)
    for rec in trace_record.get("recommendations", []):
        if rec.get("type", "").startswith("sp_"):
            findings.append({
                "type": "sticky_policy_alert",
                "policy_issue": rec.get("type"),
                "severity": rec.get("severity"),
                "message": rec.get("message"),
                "recommended_action": "Organizational / governance action required"
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
