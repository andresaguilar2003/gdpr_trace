# 🛡️ GDPR Trace Compliance Framework

Una herramienta experimental para **evaluar, simular y mejorar el cumplimiento del RGPD (GDPR)** en *event logs* de procesos de negocio, basada en **Process Mining**.

---

## 📌 Motivación

En la práctica, **no existen logs reales con eventos GDPR explícitos** (consentimiento, brechas, derechos del interesado, etc.). Esto dificulta:

* Analizar el cumplimiento normativo
* Detectar violaciones
* Evaluar riesgos
* Proponer acciones correctivas

Este proyecto aborda ese problema generando **trazas GDPR sintéticas** a partir de logs reales y proporcionando **métricas, recomendaciones y simulaciones de remediación**.

---

## 🧠 Idea Principal

A partir de un *event log* real:

1. Se genera una versión **GDPR-compliant** de cada traza
2. Se introduce ruido controlado para crear una versión **non-compliant**
3. Se validan violaciones GDPR
4. Se generan recomendaciones automáticas
5. Se calcula un **GDPR Risk Score**
6. Se simulan correcciones (*remediation*)
7. Se compara el estado **Before vs After**

---

## 🏗️ Arquitectura del Sistema

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

## ⚖️ Validaciones GDPR Implementadas

* ✅ Consentimiento antes del acceso a datos
* ✅ Retirada de consentimiento
* ✅ Restricción del tratamiento
* ✅ Notificación de brechas ≤ 72h
* ✅ Derechos del interesado (acceso / información ≤ 30 días)
* ✅ Coherencia temporal entre eventos

---

## 📊 GDPR Risk Scoring

Cada traza recibe un **risk score cuantitativo** basado en:

| Severidad | Peso |
| --------- | ---- |
| Critical  | 4    |
| High      | 3    |
| Medium    | 2    |
| Low       | 1    |

Clasificación:

* `0–29` → Low
* `30–69` → Medium
* `70–100` → High

---

## 🔁 Simulación de Remediación (Opción C)

El sistema **aplica automáticamente recomendaciones** sobre trazas no conformes para simular cómo debería corregirse el proceso.

Esto permite:

* Re-validar el cumplimiento
* Re-calcular el riesgo
* Medir la mejora obtenida

---

## 📈 Gráfica Before vs After

Se genera automáticamente una gráfica que compara:

* Riesgo medio **antes** de la remediación
* Riesgo medio **después** de la remediación

📌 Esto demuestra visualmente el impacto de las acciones correctivas.

---

## 👤 Autor

**Andrés Aguilar**
Universidad de Castilla-La Mancha

