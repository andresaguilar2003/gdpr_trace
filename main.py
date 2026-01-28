from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog
import os
import matplotlib.pyplot as plt
from collections import Counter

from gdpr.importers import load_event_log
from gdpr.pipelines import (
    build_compliant_trace,
    build_non_compliant_trace
)
from gdpr.validators.validators import (
    validate_trace,
    annotate_violations_on_trace
)
from gdpr.recommendations import (
    generate_recommendations,
    generate_sp_recommendations
)
from gdpr.scoring import compute_gdpr_risk_score, classify_risk
from gdpr.remediation import apply_recommendations
from gdpr.sticky_policies import build_sticky_policy_from_trace
from gdpr.exporters import export_recommendations, export_markdown_report, export_pdf_report
from gdpr.reporting import build_gdpr_analysis_report, build_gdpr_executive_report


# ============================================================
# CONFIGURACIÓN
# ============================================================

INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
log_filename = "Sepsis Cases - Event Log.xes.gz"

log_path = os.path.join(INPUT_DIR, log_filename)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CARGA DEL LOG
# ============================================================

log = load_event_log(log_path)

print(f"Número de trazas: {len(log)}")
print(f"Número de eventos de la primera traza: {len(log[0])}")


# ============================================================
# CONTEXTO GDPR A NIVEL DE TRAZA
# ============================================================

for trace in log:
    trace.attributes.update({
        "gdpr:personal_data": True,
        "gdpr:data_category": "unspecified",
        "gdpr:processing_context": "generic",
        "gdpr:legal_basis": "consent",
        "gdpr:default_purpose": "service_provision"
    })


# ============================================================
# PIPELINE GDPR
# ============================================================

compliant_log = []
non_compliant_log = []
remediated_log = []
trace_evidence = []

violation_counter = Counter()

for trace in log:

    # 1️⃣ COMPLIANT
    compliant = build_compliant_trace(trace)
    compliant.attributes["gdpr:sticky_policy"] = (
        build_sticky_policy_from_trace(compliant)
    )
    compliant_log.append(compliant)

    # 2️⃣ NON-COMPLIANT
    non_compliant = build_non_compliant_trace(compliant)
    non_compliant.attributes["gdpr:sticky_policy"] = (
        build_sticky_policy_from_trace(non_compliant)
    )
    non_compliant_log.append(non_compliant)

    # 3️⃣ VALIDACIÓN
    violations = validate_trace(non_compliant)

    # ⬅️ NUEVO: contar violaciones
    for v in violations:
        violation_counter[v["type"]] += 1

    annotate_violations_on_trace(non_compliant, violations)

    # 4️⃣ RECOMENDACIONES
    recommendations = generate_recommendations(violations)
    recommendations.extend(
        generate_sp_recommendations(non_compliant)
    )

    # 5️⃣ SCORING
    risk_score = compute_gdpr_risk_score(recommendations)
    risk_level = classify_risk(risk_score)

    non_compliant.attributes.update({
        "gdpr:risk_score": risk_score,
        "gdpr:risk_level": risk_level
    })

    # 6️⃣ REMEDIATION
    remediated = apply_recommendations(non_compliant, recommendations)
    remediated.attributes["gdpr:sticky_policy"] = (
        build_sticky_policy_from_trace(remediated)
    )
    remediated_log.append(remediated)

    # 7️⃣ REVALIDACIÓN
    corrected_violations = validate_trace(remediated)
    corrected_recommendations = generate_recommendations(
        corrected_violations
    )

    corrected_score = compute_gdpr_risk_score(
        corrected_recommendations
    )
    corrected_level = classify_risk(corrected_score)

    trace_evidence.append({
        "trace_id": non_compliant.attributes.get("concept:name"),

        # 🔴 ESTADO BASE PARA ANÁLISIS
        "violations": violations,
        "recommendations": recommendations,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "sticky_policy": non_compliant.attributes.get("gdpr:sticky_policy"),

        # 🔵 CONTEXTO ADICIONAL (no analítico)
        "initial_state": {
            "violations": violations,
            "risk_score": risk_score,
            "risk_level": risk_level
        },
        "post_remediation_state": {
            "violations": corrected_violations,
            "risk_score": corrected_score,
            "risk_level": corrected_level
        },

        "remediation": {
            "corrected_violations": corrected_violations
        }
    })

# ============================================================
# RESUMEN GLOBAL DE VIOLACIONES
# ============================================================

print("\n=== DISTRIBUCIÓN DE VIOLACIONES ===")
for vtype, count in violation_counter.most_common():
    print(f"{vtype}: {count}")


# ============================================================
# EXPORTACIÓN
# ============================================================

base_name = os.path.splitext(log_filename)[0]
output_subdir = os.path.join(OUTPUT_DIR, base_name)
os.makedirs(output_subdir, exist_ok=True)

print(f"Exportando resultados en: {output_subdir}")


# ----------------------------
# XES
# ----------------------------

xes_exporter.apply(
    EventLog(compliant_log),
    os.path.join(output_subdir, f"{base_name}_GDPR_compliant.xes")
)
xes_exporter.apply(
    EventLog(non_compliant_log),
    os.path.join(output_subdir, f"{base_name}_GDPR_NON_compliant.xes")
)
xes_exporter.apply(
    EventLog(remediated_log),
    os.path.join(output_subdir, f"{base_name}_GDPR_REMEDIATED.xes")
)

print("Logs XES exportados correctamente.")


# ============================================================
# INFORME TÉCNICO (JSON)
# ============================================================

technical_report = build_gdpr_analysis_report(
    trace_evidence,
    log_filename
)

json_path = export_recommendations(
    technical_report,
    output_subdir,
    filename=f"{base_name}_gdpr_case_analysis.json"
)

print("Informe técnico GDPR exportado:")
print(" -", json_path)


# ============================================================
# INFORME EJECUTIVO (MD + PDF)
# ============================================================

executive_report = build_gdpr_executive_report(
    trace_evidence,
    log_filename
)

md_path = export_markdown_report(
    executive_report,
    output_subdir,
    filename=f"{base_name}_gdpr_case_analysis.md"
)

pdf_path = export_pdf_report(md_path)

print("Informe ejecutivo GDPR exportado:")
print(" - Markdown:", md_path)
print(" - PDF:", pdf_path)


# ----------------------------
# GRÁFICA BEFORE vs AFTER
# ----------------------------

before_avg = sum(
    t["initial_state"]["risk_score"] for t in trace_evidence
) / len(trace_evidence)

after_avg = sum(
    t["post_remediation_state"]["risk_score"] for t in trace_evidence
) / len(trace_evidence)

plt.figure()
plt.bar(
    ["Before remediation", "After remediation"],
    [before_avg, after_avg]
)

plt.title("GDPR Risk Score – Before vs After Remediation")
plt.ylabel("Risk score")

plot_path = os.path.join(
    output_subdir,
    f"{base_name}_gdpr_risk_before_after.png"
)

plt.savefig(plot_path)
plt.close()

print("Gráfica GDPR Before vs After exportada en:")
print(" -", plot_path)
