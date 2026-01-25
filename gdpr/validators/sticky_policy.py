"""
Validación normativa de Sticky Policies (SP).

La Sticky Policy se considera:
- Evidencia normativa (NO se modifica)
- Estado global del dato personal
- Fuente de responsabilidad (accountability)
"""

from datetime import datetime


# ============================================================
# ENTRY POINT
# ============================================================

def validate_sticky_policy(trace):
    """
    Valida la Sticky Policy asociada a una traza GDPR.

    Retorna una lista de violaciones GDPR.
    """
    violations = []

    sp = trace.attributes.get("gdpr:sticky_policy")
    if not sp:
        return violations

    violations.extend(validate_sp_internal_consistency(sp))
    violations.extend(validate_sp_retention(sp))
    violations.extend(validate_sp_purpose_limitation(trace, sp))
    violations.extend(validate_sp_access_constraints(trace, sp))
    violations.extend(validate_sp_obligations(trace, sp))
    violations.extend(validate_sp_third_parties(sp))

    return violations


# ============================================================
# 1. COHERENCIA INTERNA (Art. 5.1.a, 5.2)
# ============================================================

def validate_sp_internal_consistency(sp):
    violations = []

    if sp.consent_given and not sp.consent_timestamp:
        violations.append({
            "type": "sp_missing_consent_timestamp",
            "severity": "high",
            "message": "Consentimiento marcado como válido sin timestamp",
            "events": []
        })

    if sp.consent_expired and not sp.consent_given:
        violations.append({
            "type": "sp_consent_expired_without_consent",
            "severity": "medium",
            "message": "Consentimiento expirado sin haber sido otorgado",
            "events": []
        })

    if sp.erased and sp.processing_restricted:
        violations.append({
            "type": "sp_invalid_state_after_erasure",
            "severity": "medium",
            "message": "Restricción de tratamiento activa tras el borrado",
            "events": []
        })

    return violations


# ============================================================
# 2. RETENCIÓN (Art. 5.1.e)
# ============================================================

def validate_sp_retention(sp):
    violations = []

    if not sp.max_retention_time:
        return violations

    for entry in sp.access_history:
        if entry["timestamp"] > sp.max_retention_time:
            violations.append({
                "type": "sp_retention_violation",
                "severity": "critical",
                "message": "Acceso a datos tras el periodo máximo de retención",
                "events": []
            })
            break

    return violations


# ============================================================
# 3. LIMITACIÓN DE PROPÓSITO (Art. 5.1.b)
# ============================================================

def validate_sp_purpose_limitation(trace, sp):
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
# 4. ACCESO SEGÚN ESTADO DE LA SP (Art. 6, 17, 18)
# ============================================================

def validate_sp_access_constraints(trace, sp):
    violations = []

    for event in trace:
        if not event.get("gdpr:access"):
            continue

        ts = event["time:timestamp"]

        if sp.erasure_timestamp and ts > sp.erasure_timestamp:
            violations.append({
                "type": "sp_access_after_erasure",
                "severity": "critical",
                "message": "Acceso a datos tras el borrado completo",
                "events": [event]
            })

        elif sp.processing_restricted:
            violations.append({
                "type": "sp_access_during_restriction",
                "severity": "high",
                "message": "Acceso a datos durante restricción de tratamiento",
                "events": [event]
            })

        elif sp.consent_expiration_timestamp and ts > sp.consent_expiration_timestamp:
            violations.append({
                "type": "sp_access_after_consent_expiration",
                "severity": "high",
                "message": "Acceso a datos tras la expiración del consentimiento",
                "events": [event]
            })

    return violations


# ============================================================
# 5. OBLIGACIONES (Art. 5.2 – Accountability)
# ============================================================

def validate_sp_obligations(trace, sp):
    violations = []

    if "log_access" not in sp.obligations:
        return violations

    for event in trace:
        if not event.get("gdpr:access"):
            continue

        has_log = any(
            e["concept:name"] == "gdpr:accessLog"
            and e["time:timestamp"] >= event["time:timestamp"]
            for e in trace
        )

        if not has_log:
            violations.append({
                "type": "sp_missing_access_log",
                "severity": "medium",
                "message": "Acceso sin cumplimiento de la obligación de logging",
                "events": [event]
            })

    return violations


# ============================================================
# 6. TERCEROS – VALIDACIÓN SP-ONLY (Art. 17, 19, 26–28, 44)
# ============================================================

def validate_sp_third_parties(sp):
    """
    Validación normativa de terceros basada únicamente en la Sticky Policy.
    """
    violations = []

    # Usamos el último instante conocido de la SP
    now = max(
        (
            tp.get("retention_until")
            for tp in sp.third_parties.values()
            if tp.get("retention_until")
        ),
        default=sp.erasure_timestamp or sp.consent_expiration_timestamp
    )

    for tp_name, tp in sp.third_parties.items():
        active = tp.get("active", False)
        role = tp.get("role", "processor")

        # ----------------------------------------------------
        # Consentimiento (Art. 6)
        # ----------------------------------------------------
        if active and not sp.consent_given:
            violations.append({
                "type": "sp_third_party_without_consent",
                "severity": "critical",
                "message": f"Tercero '{tp_name}' activo sin consentimiento válido",
                "events": []
            })

        # ----------------------------------------------------
        # Borrado y propagación (Art. 17 y 19)
        # ----------------------------------------------------
        if sp.erased and active:
            violations.append({
                "type": "sp_third_party_after_erasure",
                "severity": "critical",
                "message": f"Tercero '{tp_name}' sigue activo tras el borrado",
                "events": []
            })

        if sp.erased and not tp.get("notified_of_erasure", False):
            violations.append({
                "type": "sp_third_party_not_notified_of_erasure",
                "severity": "high",
                "message": f"Tercero '{tp_name}' no fue notificado del borrado",
                "events": []
            })

        # ----------------------------------------------------
        # Rol jurídico (Art. 26–28)
        # ----------------------------------------------------
        if role == "independent_controller" and not tp.get("legal_basis"):
            violations.append({
                "type": "sp_third_party_missing_legal_basis",
                "severity": "critical",
                "message": f"Tercero '{tp_name}' como responsable independiente sin base legal",
                "events": []
            })

        if role == "processor" and tp.get("own_legal_basis"):
            violations.append({
                "type": "sp_processor_with_own_legal_basis",
                "severity": "high",
                "message": f"Encargado '{tp_name}' declara base legal propia",
                "events": []
            })

        # ----------------------------------------------------
        # Transferencias internacionales (Art. 44–49)
        # ----------------------------------------------------
        if tp.get("country") and tp["country"] != "EU":
            if not tp.get("transfer_mechanism"):
                violations.append({
                    "type": "sp_illegal_international_transfer",
                    "severity": "critical",
                    "message": f"Transferencia internacional sin salvaguardas a '{tp_name}'",
                    "events": []
                })

        # ----------------------------------------------------
        # Retención del tercero
        # ----------------------------------------------------
        retention_until = tp.get("retention_until")

        # Tomamos como referencia temporal el contexto de la SP
        reference_time = (
            sp.erasure_timestamp
            or sp.consent_expiration_timestamp
            or retention_until
        )

        if active and retention_until and reference_time:
            if reference_time > retention_until:
                violations.append({
                    "type": "sp_third_party_retention_violation",
                    "severity": "high",
                    "message": (
                        f"Tercero '{tp_name}' supera el periodo de retención autorizado"
                    ),
                    "events": []
                })


        # ----------------------------------------------------
        # Minimización de permisos (Art. 5.1.c)
        # ----------------------------------------------------
        if not tp.get("permissions", set()).issubset(sp.permissions):
            violations.append({
                "type": "sp_third_party_permission_escalation",
                "severity": "high",
                "message": f"Tercero '{tp_name}' tiene permisos no autorizados",
                "events": []
            })

        # ----------------------------------------------------
        # Propósitos del tercero
        # ----------------------------------------------------
        for p in tp.get("purposes", set()):
            if p not in sp.purposes:
                violations.append({
                    "type": "sp_third_party_purpose_violation",
                    "severity": "high",
                    "message": f"Tercero '{tp_name}' usa propósito no autorizado",
                    "events": []
                })

    return violations
