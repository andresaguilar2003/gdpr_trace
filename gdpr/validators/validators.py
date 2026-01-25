from .phase1_consent import validate_implicit_consent, validate_consent_before_access
from .phase2_processing_loop import validate_access_after_consent_expiration,validate_withdrawn_consent
from .phase3_rights import validate_processing_restriction, validate_erase_without_processing, validate_access_after_erasure, validate_access_log_without_access
from .phase4_accountability import validate_data_minimization, validate_purpose_limitation, validate_access_without_permission, validate_missing_access_log
from .phase5_breach import validate_breach_notification_time
from .phase6_rights_arco import validate_data_subject_rights
from .sticky_policy import validate_sticky_policy

def annotate_violations_on_trace(trace, violations):
    """
    Marca los eventos de la traza que causan violaciones GDPR.
    Compatible con pm4py Event.
    """
    for v in violations:
        for event in v.get("events", []):

            # Inicializar lista si no existe
            if "gdpr:violations" not in event:
                event["gdpr:violations"] = []

            event["gdpr:violations"].append({
                "type": v["type"],
                "severity": v.get("severity", "unknown"),
                "message": v.get("message")
            })

            # Campos planos (útiles para XES simples)
            event["gdpr:violation_severity"] = v.get("severity", "unknown")
            event["gdpr:violation_message"] = v.get("message")


def deduplicate_sp_violations(violations):
    sp_types = {
        v["type"].replace("sp_", "")
        for v in violations
        if v["type"].startswith("sp_")
    }

    filtered = []
    for v in violations:
        if v["type"] in sp_types:
            continue  # absorbida por SP
        filtered.append(v)

    return filtered


def validate_trace(trace):
    violations = []
    violations.extend(validate_consent_before_access(trace))
    violations.extend(validate_implicit_consent(trace))
    violations.extend(validate_access_after_consent_expiration(trace))
    violations.extend(validate_withdrawn_consent(trace))
    violations.extend(validate_processing_restriction(trace))
    violations.extend(validate_erase_without_processing(trace))
    violations.extend(validate_access_after_erasure(trace))
    violations.extend(validate_access_log_without_access(trace))
    violations.extend(validate_data_minimization(trace))
    violations.extend(validate_purpose_limitation(trace))
    violations.extend(validate_access_without_permission(trace))
    violations.extend(validate_missing_access_log(trace))
    violations.extend(validate_breach_notification_time(trace))
    violations.extend(validate_data_subject_rights(trace))
    violations.extend(validate_sticky_policy(trace))


    return violations
