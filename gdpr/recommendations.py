# gdpr/recommendations.py

RECOMMENDATION_CATALOG = {
    "consent_after_access": {
        "severity": "high",
        "risk_level": "critical",
        "title": "Solicitar consentimiento antes del tratamiento",
        "recommendation": (
            "El consentimiento del interesado debe obtenerse de forma explícita "
            "antes de cualquier acceso o tratamiento de datos personales."
        ),
        "legal_reference": "Art. 6 y Art. 7 GDPR",
        "suggested_events_order": [
            "gdpr:inform",
            "gdpr:consent",
            "gdpr:permissionGranted",
            "data_access"
        ]
    },

    "access_after_withdrawal": {
        "severity": "medium",
        "risk_level": "critical",
        "title": "Cesar el tratamiento tras retirada del consentimiento",
        "recommendation": (
            "Una vez retirado el consentimiento, el responsable debe cesar "
            "inmediatamente cualquier acceso o tratamiento de datos personales."
        ),
        "legal_reference": "Art. 7.3 GDPR",
        "suggested_events_order": [
            "gdpr:withdraw",
            "no_data_access"
        ]
    },

    "access_during_restriction": {
        "severity": "high",
        "risk_level": "critical",
        "title": "Respetar la restricción del tratamiento",
        "recommendation": (
            "Durante un periodo de restricción del tratamiento, no deben realizarse "
            "operaciones de acceso o modificación de datos."
        ),
        "legal_reference": "Art. 18 GDPR",
        "suggested_events_order": [
            "gdpr:restrictProcessing",
            "gdpr:liftRestriction"
        ]
    },

    "late_breach_notification": {
        "severity": "medium",
        "risk_level": "critical",
        "title": "Notificar brechas de seguridad en plazo",
        "recommendation": (
            "Las brechas de seguridad deben notificarse a la autoridad competente "
            "en un plazo máximo de 72 horas desde su detección."
        ),
        "legal_reference": "Art. 33 GDPR",
        "time_constraint": "≤ 72 hours"
    },

    "missing_right_response": {
        "severity": "medium",
        "risk_level": "procedural",
        "title": "Responder a los derechos del interesado",
        "recommendation": (
            "Las solicitudes de acceso o información del interesado deben ser "
            "atendidas en un plazo máximo de 30 días."
        ),
        "legal_reference": "Art. 12 y Art. 15 GDPR",
        "time_constraint": "≤ 30 days"
    },

    "missing_breach_notification": {
        "severity": "high",
        "risk_level": "critical",
        "title": "Notificar brechas de seguridad",
        "recommendation": (
            "Toda brecha de seguridad que afecte a datos personales debe "
            "ser notificada a la autoridad competente."
        ),
        "legal_reference": "Art. 33 GDPR"
    },

    "late_right_response": {
        "severity": "medium",
        "risk_level": "procedural",
        "title": "Responder a los derechos en plazo",
        "recommendation": (
            "Las solicitudes del interesado deben resolverse "
            "en un plazo máximo de 30 días."
        ),
        "legal_reference": "Art. 12 GDPR",
        "time_constraint": "≤ 30 days"
    },

    "erase_without_processing": {
        "severity": "low",
        "risk_level": "incoherent_process",
        "title": "Coherencia del ciclo de vida de los datos",
        "recommendation": (
            "No debe solicitarse el borrado de datos si no consta "
            "ningún tratamiento previo de los mismos."
        ),
        "legal_reference": "Art. 5 GDPR"
    }

}


def generate_recommendations(violations):
    """
    Genera recomendaciones GDPR a partir de violaciones detectadas.
    """
    recommendations = []

    for v in violations:
        v_type = v["type"]

        # Caso 1: existe recomendación conocida
        if v_type in RECOMMENDATION_CATALOG:
            base = RECOMMENDATION_CATALOG[v_type]

            recommendations.append({
                "violation": v_type,
                "severity": base.get("severity"),
                "risk_level": base.get("risk_level"),
                "title": base.get("title"),
                "recommendation": base.get("recommendation"),
                "legal_reference": base.get("legal_reference"),
                "suggested_events_order": base.get("suggested_events_order"),
                "time_constraint": base.get("time_constraint")
            })

        # Caso 2: violación detectada pero sin recomendación definida
        else:
            recommendations.append({
                "violation": v_type,
                "severity": "unknown",
                "risk_level": "unknown",
                "title": "Violación GDPR detectada",
                "recommendation": (
                    "Se ha detectado una posible violación del RGPD. "
                    "Revise la secuencia de eventos y los requisitos legales aplicables."
                ),
                "legal_reference": "GDPR (general)",
                "suggested_events_order": None,
                "time_constraint": None
            })

    return recommendations

