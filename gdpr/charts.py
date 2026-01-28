# gdpr/charts.py

import os
import matplotlib.pyplot as plt
from collections import Counter


def generate_severity_chart(violations_summary, output_dir):
    """
    Generates a bar chart showing number of violations per severity level.
    Returns path to generated image.
    """

    severities = [v["severity"] for v in violations_summary if v.get("severity")]
    counts = Counter(severities)

    # Ensure consistent ordering
    order = ["low", "medium", "high"]
    values = [counts.get(level, 0) for level in order]

    plt.figure(figsize=(6, 4))
    plt.bar(order, values)
    plt.title("GDPR Violations by Severity")
    plt.xlabel("Severity level")
    plt.ylabel("Number of violations")

    os.makedirs(output_dir, exist_ok=True)
    chart_path = os.path.join(output_dir, "gdpr_severity_overview.png")

    plt.tight_layout()
    plt.savefig(chart_path, dpi=200)
    plt.close()

    return chart_path
