from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog
import os

from gdpr.pipelines import (
    build_compliant_trace,
    build_non_compliant_trace
)
from gdpr.validators.validators import validate_trace
from gdpr.recommendations import generate_recommendations, generate_sp_recommendations
from gdpr.summary import summarize_recommendations
from gdpr.exporters import export_recommendations
from gdpr.scoring import compute_gdpr_risk_score, classify_risk
from gdpr.validators.validators import validate_trace, annotate_violations_on_trace
from gdpr.ranking import build_trace_ranking
from gdpr.audit import generate_audit_report
from gdpr.remediation import apply_recommendations
from gdpr.sticky_policies import build_sticky_policy_from_trace


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

from gdpr.importers import load_event_log

log = load_event_log(log_path)

print(f"Número de trazas: {len(log)}")
print(f"Número de eventos de la primera traza: {len(log[0])}")


# ============================================================
# CONTEXTO GDPR A NIVEL DE TRAZA
# ============================================================

for trace in log:
    trace.attributes["gdpr:personal_data"] = True
    trace.attributes["gdpr:data_category"] = "unspecified"
    trace.attributes["gdpr:processing_context"] = "generic"
    trace.attributes["gdpr:legal_basis"] = "consent"
    trace.attributes["gdpr:default_purpose"] = "service_provision"


# ============================================================
# PIPELINES + VALIDACIÓN + RECOMENDACIONES
# ============================================================

compliant_log = []
non_compliant_log = []
remediated_log = []
all_recommendations = []

for trace in log:
    # 1️⃣ Traza compliant
    compliant = build_compliant_trace(trace)

    # 🟢 SP (después de construir la compliant)
    compliant_sp = build_sticky_policy_from_trace(compliant)
    compliant.attributes["gdpr:sticky_policy"] = compliant_sp

    compliant_log.append(compliant)

    # 2️⃣ Traza non-compliant
    non_compliant = build_non_compliant_trace(compliant)

    # 🟢 SP (después de generar violaciones)
    non_compliant_sp = build_sticky_policy_from_trace(non_compliant)
    non_compliant.attributes["gdpr:sticky_policy"] = non_compliant_sp

    non_compliant_log.append(non_compliant)

    # 3️⃣ Validación
    violations = validate_trace(non_compliant)
    annotate_violations_on_trace(non_compliant, violations)

    # 4️⃣ Recomendaciones
    recommendations = generate_recommendations(violations)

    sp_recommendations = generate_sp_recommendations(non_compliant)
    recommendations.extend(sp_recommendations)


    # 5️⃣ GDPR RISK SCORING
    risk_score = compute_gdpr_risk_score(recommendations)
    risk_level = classify_risk(risk_score)

    non_compliant.attributes["gdpr:risk_score"] = risk_score
    non_compliant.attributes["gdpr:risk_level"] = risk_level

    # 6️⃣ SIMULACIÓN CORRECTIVA
    remediated = apply_recommendations(non_compliant, recommendations)

    # 🟢 SP (después de remediation)
    remediated_sp = build_sticky_policy_from_trace(remediated)
    remediated.attributes["gdpr:sticky_policy"] = remediated_sp

    remediated_log.append(remediated)

    # 7️⃣ Re-validación
    remediated_violations = validate_trace(remediated)
    remediated_recommendations = generate_recommendations(remediated_violations)


    # 8️⃣ GDPR RISK SCORING (DESPUÉS)
    remediated_score = compute_gdpr_risk_score(remediated_recommendations)
    remediated_level = classify_risk(remediated_score)

    # 9️⃣ Guardar resultados completos

    all_recommendations.append({
        "trace_id": non_compliant.attributes.get("concept:name"),
        "violations": violations,
        "recommendations": recommendations,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "remediation": {
            "corrected_violations": remediated_violations,
            "corrected_risk_score": remediated_score,
            "corrected_risk_level": remediated_level,
            "improvement": risk_score - remediated_score
        }
    })



# ============================================================
# CREAR SUBCARPETA PARA ESTE INPUT
# ============================================================

base_name = os.path.splitext(log_filename)[0]

output_subdir = os.path.join(OUTPUT_DIR, base_name)
os.makedirs(output_subdir, exist_ok=True)

print(f"Exportando resultados en: {output_subdir}")


# ============================================================
# EXPORTAR LOGS XES
# ============================================================

compliant_event_log = EventLog(compliant_log)
non_compliant_event_log = EventLog(non_compliant_log)
remediated_event_log = EventLog(remediated_log)

compliant_path = os.path.join(
    output_subdir, f"{base_name}_GDPR_compliant.xes"
)
non_compliant_path = os.path.join(
    output_subdir, f"{base_name}_GDPR_NON_compliant.xes"
)
remediated_path = os.path.join(
    output_subdir, f"{base_name}_GDPR_REMEDIATED.xes"
)

xes_exporter.apply(compliant_event_log, compliant_path)
xes_exporter.apply(non_compliant_event_log, non_compliant_path)
xes_exporter.apply(remediated_event_log, remediated_path)

print("Logs exportados:")
print(" -", compliant_path)
print(" -", non_compliant_path)
print(" -", remediated_path)


# ============================================================
# EXPORTAR RECOMENDACIONES
# ============================================================

recommendations_path = export_recommendations(
    all_recommendations,
    output_subdir,
    filename=f"{base_name}_recommendations.json"
)

print("Recomendaciones exportadas en:")
print(" -", recommendations_path)


# ============================================================
# EXPORTAR RESUMEN GDPR
# ============================================================

summary = summarize_recommendations(all_recommendations)

summary_path = export_recommendations(
    summary,
    output_subdir,
    filename=f"{base_name}_gdpr_summary.json"
)

print("Resumen GDPR exportado en:")
print(" -", summary_path)

# ============================================================
# EXPORTAR RANKING GDPR DE TRAZAS
# ============================================================

ranking = build_trace_ranking(all_recommendations)

ranking_path = export_recommendations(
    ranking,
    output_subdir,
    filename=f"{base_name}_gdpr_trace_ranking.json"
)

print("Ranking GDPR exportado en:")
print(" -", ranking_path)

# ============================================================
# EXPORTAR INFORMES DE AUDITORÍA GDPR
# ============================================================

audit_reports = []

for trace_rec in all_recommendations:
    audit_reports.append(generate_audit_report(trace_rec))

audit_path = export_recommendations(
    audit_reports,
    output_subdir,
    filename=f"{base_name}_gdpr_audit_report.json"
)

print("Informe de auditoría GDPR exportado en:")
print(" -", audit_path)

# ============================================================
# GRÁFICA GDPR RISK — BEFORE vs AFTER
# ============================================================

import matplotlib.pyplot as plt

before_scores = []
after_scores = []

for tr in all_recommendations:
    before_scores.append(tr["risk_score"])

    remediation = tr.get("remediation")
    if remediation and "corrected_risk_score" in remediation:
        after_scores.append(remediation["corrected_risk_score"])
    else:
        after_scores.append(tr["risk_score"])



# Media global
before_avg = sum(before_scores) / len(before_scores)
after_avg = sum(after_scores) / len(after_scores)

plt.figure()
plt.bar(["Before remediation", "After remediation"],
        [before_avg, after_avg])

plt.title("GDPR Risk Score – Before vs After Remediation")
plt.ylabel("Risk score")
plt.xlabel("State")

# Guardar imagen
plot_path = os.path.join(
    output_subdir,
    f"{base_name}_gdpr_risk_before_after.png"
)

plt.savefig(plot_path)
plt.close()

print("Gráfica GDPR Before vs After exportada en:")
print(" -", plot_path)
