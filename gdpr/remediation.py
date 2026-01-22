from copy import deepcopy
from datetime import timedelta
from gdpr.vocabulary import GDPR_EVENTS

def _fix_consent_order(trace):
    consent = None
    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent = e
            break

    if not consent:
        return

    consent_ts = consent["time:timestamp"]

    for e in trace:
        if e.get("gdpr:access") and e["time:timestamp"] < consent_ts:
            e["time:timestamp"] = consent_ts + timedelta(seconds=1)


def _fix_withdrawal_access(trace):
    withdrawn = False

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["WITHDRAW"]:
            withdrawn = True

        if withdrawn and e.get("gdpr:access"):
            e["gdpr:access"] = False


def _fix_restriction_access(trace):
    restricted = False

    for e in trace:
        name = e["concept:name"]

        if name == GDPR_EVENTS["RESTRICT"]:
            restricted = True
        elif name == GDPR_EVENTS["LIFT_RESTRICTION"]:
            restricted = False
        elif restricted and e.get("gdpr:access"):
            e["gdpr:access"] = False


def _fix_breach_notification(trace):
    detects = [e for e in trace if e["concept:name"] == GDPR_EVENTS["BREACH"]]
    notifies = [e for e in trace if e["concept:name"] == GDPR_EVENTS["NOTIFY_BREACH"]]

    for d in detects:
        if not any(n["time:timestamp"] > d["time:timestamp"] for n in notifies):
            new_notify = deepcopy(d)
            new_notify["concept:name"] = GDPR_EVENTS["NOTIFY_BREACH"]
            new_notify["time:timestamp"] = d["time:timestamp"] + timedelta(hours=1)
            trace.append(new_notify)


def _fix_rights_response(trace):
    requests = [e for e in trace if e["concept:name"] == GDPR_EVENTS["REQUEST_INFO"]]
    responses = [e for e in trace if e["concept:name"] == GDPR_EVENTS["PROVIDE_INFO"]]

    for r in requests:
        if not any(resp["time:timestamp"] > r["time:timestamp"] for resp in responses):
            new_resp = deepcopy(r)
            new_resp["concept:name"] = GDPR_EVENTS["PROVIDE_INFO"]
            new_resp["time:timestamp"] = r["time:timestamp"] + timedelta(days=1)
            trace.append(new_resp)

def _fix_implicit_consent(trace):
    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            e["gdpr:explicit"] = True

def _fix_purpose_violation(trace):
    for e in trace:
        if e.get("gdpr:access"):
            e["gdpr:purpose"] = trace.attributes.get(
                "gdpr:default_purpose", "service_provision"
            )
            
def _fix_data_minimization(trace):
    for e in trace:
        if e.get("gdpr:access"):
            e["gdpr:data_scope"] = "minimal"

def _fix_access_after_erasure(trace):
    erased = False

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["ERASE"]:
            erased = True
        elif erased and e.get("gdpr:access"):
            e["gdpr:access"] = False

def _fix_missing_consent(trace):
    if any(e["concept:name"] == GDPR_EVENTS["CONSENT"] for e in trace):
        return

    first_event = trace[0]
    consent = deepcopy(first_event)
    consent["concept:name"] = GDPR_EVENTS["CONSENT"]
    consent["time:timestamp"] -= timedelta(seconds=1)
    trace.insert(0, consent)


def _fix_missing_breach_notification(trace):
    _fix_breach_notification(trace)


def _fix_late_right_response(trace):
    requests = [e for e in trace if e["concept:name"] == GDPR_EVENTS["REQUEST_INFO"]]
    responses = [e for e in trace if e["concept:name"] == GDPR_EVENTS["PROVIDE_INFO"]]

    for r in requests:
        for resp in responses:
            if resp["time:timestamp"] > r["time:timestamp"] + timedelta(days=30):
                resp["time:timestamp"] = r["time:timestamp"] + timedelta(days=1)

def _fix_access_after_consent_expiration(trace):
    expired = False

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT_EXPIRED"]:
            expired = True
        elif expired and e.get("gdpr:access"):
            e["gdpr:access"] = False

def _fix_missing_permission(trace):
    from copy import deepcopy
    from datetime import timedelta

    i = 0
    while i < len(trace):
        e = trace[i]

        if e.get("gdpr:access"):
            prev = trace[i - 1] if i > 0 else None

            if not prev or prev["concept:name"] != "gdpr:permissionGranted":
                perm = deepcopy(e)
                perm["concept:name"] = "gdpr:permissionGranted"
                perm["time:timestamp"] = e["time:timestamp"] - timedelta(seconds=1)
                perm["gdpr:event"] = True
                trace.insert(i, perm)
                i += 1

        i += 1


def apply_recommendations(trace, recommendations):
    """
    Aplica de forma SIMULADA las recomendaciones GDPR
    y devuelve una nueva traza corregida.
    """
    corrected_trace = deepcopy(trace)

    for rec in recommendations:
        v = rec["violation"]

        if v == "consent_after_access":
            _fix_consent_order(corrected_trace)

        elif v == "access_after_withdrawal":
            _fix_withdrawal_access(corrected_trace)

        elif v == "access_during_restriction":
            _fix_restriction_access(corrected_trace)

        elif v == "late_breach_notification":
            _fix_breach_notification(corrected_trace)

        elif v == "missing_right_response":
            _fix_rights_response(corrected_trace)
        
        elif v == "implicit_consent":
            _fix_implicit_consent(corrected_trace)

        elif v == "purpose_violation":
            _fix_purpose_violation(corrected_trace)

        elif v == "data_minimization_violation":
            _fix_data_minimization(corrected_trace)

        elif v == "access_after_erasure":
            _fix_access_after_erasure(corrected_trace)

        elif v == "missing_consent":
            _fix_missing_consent(corrected_trace)

        elif v == "missing_breach_notification":
            _fix_missing_breach_notification(corrected_trace)

        elif v == "late_right_response":
            _fix_late_right_response(corrected_trace)

        elif v == "access_after_consent_expiration":
            _fix_access_after_consent_expiration(corrected_trace)

        elif v == "access_without_permission":
            _fix_missing_permission(corrected_trace)



    corrected_trace.attributes["gdpr:remediated"] = True
    return corrected_trace
