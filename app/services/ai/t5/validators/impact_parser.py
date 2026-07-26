import re


IMPACT_LABELS = {
    "0": "0_COMPLIANT",
    "1": "1_VIOLATION",
    "2": "2_WARNING",
}


def parse_impact_response(response):
    """Parses a T5 impact response without silently defaulting to compliant."""
    text = (response or "").strip()
    lower_text = text.lower()
    impact_match = re.search(r"\b([012])\b", text)

    if impact_match:
        return IMPACT_LABELS[impact_match.group(1)]

    if "warning" in lower_text:
        return "2_WARNING"

    if any(token in lower_text for token in ["invalid", "violation", "violations"]):
        return "1_VIOLATION"

    if re.search(r"\bvalid\b", lower_text):
        return "0_COMPLIANT"

    return "PARSE_ERROR"


def impact_to_status(impact_label):
    return {
        "0_COMPLIANT": "valid",
        "1_VIOLATION": "invalid",
        "2_WARNING": "warning",
    }.get(impact_label, "parse_error")
