# 🛡️ GDPR Trace Compliance Framework

A research-oriented framework to **evaluate, simulate, and improve GDPR compliance**
in **business process event logs**, based on **Process Mining techniques**.

The framework enables **automated GDPR violation detection, legal risk scoring,
recommendation generation, remediation simulation, and executive-grade reporting**.

---

## 📌 Motivation

In real-world information systems, **event logs do not explicitly record GDPR-related events**
such as consent, data subject rights, or breach notifications.

This makes it difficult to:

- Assess GDPR compliance from operational data
- Detect systematic violations
- Quantify legal risk
- Justify corrective actions with evidence

This framework addresses that gap by **enriching real event logs with GDPR semantics**
and providing a **full compliance assessment pipeline**.

---

## 🧠 Core Idea

Given a real-world process execution log:

1. Generate a **GDPR-compliant baseline**
2. Introduce controlled violations to create **non-compliant traces**
3. Detect GDPR violations automatically
4. Aggregate violations across traces and processes
5. Generate **legally grounded recommendations**
6. Compute a **quantitative GDPR Risk Score**
7. Simulate **automatic remediation**
8. Compare **Before vs After compliance**
9. Produce a **professional PDF audit report**

---

## 🏗️ System Architecture

```
data/input
 └── log_original.xes

main.py

gdpr/
 ├── pipelines.py        # Generación de trazas compliant / non-compliant
 ├── validators.py       # Validadores GDPR
 ├── recommendations.py # Generación de recomendaciones
 ├── scoring.py          # Cálculo de riesgo GDPR
 ├── remediation.py     # Simulación correctiva
 ├── summary.py          # Resumen agregado
 ├── ranking.py          # Ranking de trazas por riesgo
 ├── audit.py            # Informes de auditoría
 └── exporters.py        # Exportación JSON/XES


data/output/
 └── <log_name>/
     ├── *_GDPR_compliant.xes
     ├── *_GDPR_NON_compliant.xes
     ├── *_GDPR_REMEDIATED.xes
     ├── *_recommendations.json
     ├── *_gdpr_summary.json
     ├── *_gdpr_trace_ranking.json
     ├── *_gdpr_audit_report.json
     └── *_gdpr_risk_before_after.png
```

---

## ⚖️ GDPR Validations Implemented

The framework currently supports detection of violations related to:

- ✅ Lawful basis & consent before data access
- ✅ Withdrawal of consent
- ✅ Restriction of processing
- ✅ Third-party data access without safeguards
- ✅ Personal data breach notification ≤ 72 hours
- ✅ Data subject rights (access / information ≤ 30 days)
- ✅ Temporal consistency between GDPR-relevant events

---

## 🧑‍🤝‍🧑 Third-Party Data Processing

The framework explicitly models **third-party involvement**, allowing detection of:

- Unauthorized data sharing
- Missing legal basis for transfers
- Lack of contractual safeguards
- Responsibility misalignment between controller and processor

This enables **risk attribution beyond internal processes**.

---

## 📊 GDPR Risk Scoring

Each trace and process receives a **quantitative GDPR Risk Score**.

### Severity Weights

| Severity | Weight |
| -------- | ------ |
| Critical | 4      |
| High     | 3      |
| Medium   | 2      |
| Low      | 1      |

### Risk Classification

- **0–29** → Low Risk
- **30–69** → Medium Risk
- **70–100** → High Risk

Scores are aggregated at **trace, log, and organizational level**.

---

## 🔁 Remediation Simulation

The framework supports **automatic remediation simulation**, where detected violations
are corrected according to generated recommendations.

This enables:

- Re-validation of corrected traces
- Re-calculation of risk
- Quantification of improvement

---

## 📈 Before vs After Risk Comparison

For each execution, the framework generates a visual comparison of:

- Average GDPR risk **before remediation**
- Average GDPR risk **after remediation**

This provides **evidence-based justification** of corrective actions.

---

## 📄 Executive PDF Audit Report

A **professional, multi-section PDF report** is automatically generated, including:

- Executive overview and compliance score
- Risk level with visual indicators
- GDPR violation summary tables
- Legal article mapping
- Severity distribution charts
- Key compliance signals
- Priority recommendations
- Methodology appendix

📌 The report is designed for **DPOs, auditors, and management**, not only technical users.

---

## 👤 Author

**Andrés Aguilar**
University of Castilla-La Mancha
