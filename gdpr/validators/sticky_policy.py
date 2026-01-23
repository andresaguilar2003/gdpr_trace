# gdpr/validators/sticky_policy_validator.py

"""
Validación de Sticky Policies (SP) reconstruidas a partir de la traza.

La SP se considera:
- Evidencia normativa (NO se modifica)
- Estado global asociado a la traza
"""

# ============================================================
# ENTRY POINT
# ============================================================

def validate_sticky_policy(trace):
    """
    Valida la Sticky Policy asociada a una traza.

    Retorna una lista de violaciones GDPR.
    """
    violations = []

    sp = trace.attributes.get("gdpr:sticky_policy")
    if not sp:
        return violations  # no hay SP → no se valida

    # 1. Validaciones internas de la SP (estado inconsistente)
    violations.extend(validate_sp_internal_consistency(sp))

    # 2. Retención temporal
    violations.extend(validate_sp_retention(sp))

    # 3. Limitación de propósito
    violations.extend(validate_sp_purpose_limitation(trace, sp))

    # 4. Accesos incompatibles con el estado de la SP
    violations.extend(validate_sp_access_constraints(trace, sp))

    violations.extend(validate_sp_obligations(trace, sp))


    return violations


# ============================================================
# VALIDACIONES DE COHERENCIA INTERNA
# ============================================================

def validate_sp_internal_consistency(sp):
    """
    Comprueba incoherencias internas de la Sticky Policy.
    """
    violations = []

    if sp.consent_given and not sp.consent_timestamp:
        violations.append({
            "type": "sp_missing_consent_timestamp",
            "severity": "high",
            "message": "Consentimiento marcado como válido pero sin timestamp",
            "events": []
        })

    if sp.erased and sp.processing_restricted:
        violations.append({
            "type": "sp_invalid_post_erasure_state",
            "severity": "medium",
            "message": "Restricción de tratamiento activa tras el borrado de los datos",
            "events": []
        })

    if sp.consent_expired and not sp.consent_given:
        violations.append({
            "type": "sp_invalid_consent_expiration",
            "severity": "medium",
            "message": "Consentimiento marcado como expirado sin haber sido otorgado",
            "events": []
        })

    return violations


# ============================================================
# RETENCIÓN TEMPORAL
# ============================================================

def validate_sp_retention(sp):
    """
    Verifica que no existan accesos fuera del periodo de retención permitido.
    """
    violations = []

    if not sp.max_retention_time:
        return violations

    for entry in sp.access_history:
        if entry["timestamp"] > sp.max_retention_time:
            violations.append({
                "type": "sp_retention_violation",
                "severity": "critical",
                "message": "Acceso a datos fuera del periodo de retención permitido",
                "events": []
            })
            break  # una sola violación global

    return violations


# ============================================================
# LIMITACIÓN DE PROPÓSITO
# ============================================================

def validate_sp_purpose_limitation(trace, sp):
    """
    Comprueba que los accesos respeten los propósitos autorizados
    por la Sticky Policy.
    """
    violations = []

    for event in trace:
        if not event.get("gdpr:access"):
            continue

        purpose = event.get("gdpr:purpose")

        if purpose not in sp.purposes:
            violations.append({
                "type": "sp_purpose_violation",
                "severity": "high",
                "message": "Acceso con propósito no autorizado por la Sticky Policy",
                "events": [event]
            })

    return violations


# ============================================================
# RESTRICCIONES DE ACCESO SEGÚN ESTADO SP
# ============================================================

def validate_sp_access_constraints(trace, sp):
    """
    Valida accesos incompatibles con el estado global de la SP.
    """
    violations = []

    for event in trace:
        if not event.get("gdpr:access"):
            continue

        if sp.erased:
            violations.append({
                "type": "sp_access_after_erasure",
                "severity": "critical",
                "message": "Acceso a datos tras el borrado completo según la Sticky Policy",
                "events": [event]
            })

        elif sp.processing_restricted:
            violations.append({
                "type": "sp_access_during_restriction",
                "severity": "high",
                "message": "Acceso a datos durante una restricción de tratamiento",
                "events": [event]
            })

        elif (
            sp.consent_expiration_timestamp
            and event["time:timestamp"] > sp.consent_expiration_timestamp
        ):
            violations.append({
                "type": "sp_access_after_consent_expiration",
                "severity": "high",
                "message": "Acceso a datos tras la expiración del consentimiento",
                "events": [event]
            })


    return violations

def validate_sp_obligations(trace, sp):
    violations = []

    if "log_access" in sp.obligations:
        for event in trace:
            if event.get("gdpr:access"):
                has_log = any(
                    e["concept:name"] == "gdpr:accessLog"
                    and e["time:timestamp"] >= event["time:timestamp"]
                    for e in trace
                )
                if not has_log:
                    violations.append({
                        "type": "sp_missing_access_log",
                        "severity": "medium",
                        "message": "Acceso sin obligación de logging cumplida",
                        "events": [event]
                    })

    return violations
