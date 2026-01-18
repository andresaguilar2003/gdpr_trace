# gdpr/exporters.py

import os
import json
from datetime import datetime


def export_recommendations(data, output_dir, filename="recommendations.json"):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    clean_data = sanitize_recommendations(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    return path


# ============================================================
# SERIALIZACIÓN
# ============================================================

def serialize_event(event):
    """
    Convierte un evento pm4py en un dict JSON-serializable.
    """
    serialized = {}

    for k, v in event.items():
        if isinstance(v, datetime):
            serialized[k] = v.isoformat()
        else:
            serialized[k] = v

    return serialized


def sanitize_violation_list(violations):
    """
    Limpia una lista de violaciones (normal o remediada).
    """
    clean = []

    for v in violations:
        v_copy = dict(v)

        if "events" in v_copy:
            v_copy["events"] = [
                serialize_event(e) for e in v_copy["events"]
            ]

        clean.append(v_copy)

    return clean


def sanitize_recommendations(data):
    """
    Limpia toda la estructura de recomendaciones para JSON.
    """
    if not isinstance(data, list):
        return data

    sanitized = []

    for trace_rec in data:
        tr = dict(trace_rec)

        # Violaciones originales
        if "violations" in tr:
            tr["violations"] = sanitize_violation_list(tr["violations"])

        # Violaciones tras remediación
        remediation = tr.get("remediation")
        if remediation and "corrected_violations" in remediation:
            remediation["corrected_violations"] = sanitize_violation_list(
                remediation["corrected_violations"]
            )
            tr["remediation"] = remediation

        sanitized.append(tr)

    return sanitized
