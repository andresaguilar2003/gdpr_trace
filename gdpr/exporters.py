# gdpr/exporters.py

import os
import json
from datetime import datetime


def export_recommendations(data, output_dir, filename="recommendations.json"):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    clean_data = sanitize(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    return path


# ============================================================
# SERIALIZACIÓN GENÉRICA
# ============================================================

def serialize_event(event):
    """
    Convierte un evento pm4py en un dict JSON-serializable.
    """
    serialized = {}

    for k, v in event.items():
        serialized[k] = sanitize(v)

    return serialized


def sanitize(obj):
    """
    Limpia recursivamente cualquier estructura para JSON.
    """

    # datetime → ISO
    if isinstance(obj, datetime):
        return obj.isoformat()

    # pm4py Event (dict-like)
    if hasattr(obj, "items") and obj.__class__.__name__ == "Event":
        return serialize_event(obj)

    # dict
    if isinstance(obj, dict):
        return {
            k: sanitize(v)
            for k, v in obj.items()
        }

    # list / tuple / set
    if isinstance(obj, (list, tuple, set)):
        return [sanitize(v) for v in obj]

    # tipos básicos
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # fallback defensivo (por si aparece algo raro)
    return str(obj)
