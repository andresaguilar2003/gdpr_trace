def evaluate_trace(trace):
    issues = []

    consent_ts = None
    for e in trace:
        if e["concept:name"] == "gdpr:giveConsent":
            consent_ts = e["time:timestamp"]
        if e.get("gdpr:access") and consent_ts is None:
            issues.append("access_without_consent")
        if e.get("gdpr:access") and consent_ts and e["time:timestamp"] < consent_ts:
            issues.append("access_before_consent")

    return list(set(issues))
