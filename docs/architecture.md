# Arquitectura del Sistema

## Visión general

Este proyecto implementa un **pipeline de análisis de cumplimiento del RGPD de extremo a extremo** para registros de eventos (trazas de process mining). A partir de logs reales de ejecución de procesos, el sistema:

1. Importa registros de eventos en múltiples formatos (XES, CSV, JSON)
2. Los enriquece con contexto semántico GDPR
3. Genera variantes conformes e intencionadamente no conformes
4. Detecta violaciones del RGPD mediante validadores formales
5. Produce recomendaciones legales y operativas
6. Calcula puntuaciones de riesgo GDPR (antes y después de la corrección)
7. Simula acciones correctivas (remediación)
8. Agrega los resultados en resúmenes, rankings, informes de auditoría y analítica visual

La arquitectura es **modular**, **extensible** y está diseñada para soportar **experimentación**, **auditoría** y **explicabilidad**.

---

## Diagrama de arquitectura de alto nivel

```mermaid
flowchart TD
    A[Log de eventos de entrada
(XES / CSV / JSON)] --> B[Capa de importadores]

    B --> C[EventLog (pm4py)]

    C --> D[Enriquecimiento de contexto GDPR]

    D --> E1[Constructor de trazas conformes]
    E1 --> F1[Log conforme]

    E1 --> E2[Generador de trazas no conformes]
    E2 --> F2[Log no conforme]

    F2 --> G[Validadores GDPR]
    G --> H[Violaciones detectadas]

    H --> I[Motor de recomendaciones]
    I --> J[Recomendaciones GDPR]

    J --> K[Motor de scoring de riesgo]
    K --> L[Puntuación y nivel de riesgo
(Antes)]

    J --> M[Motor de remediación]
    M --> N[Traza remediada]

    N --> O[Re-validación]
    O --> P[Violaciones actualizadas]
    P --> Q[Recomendaciones actualizadas]
    Q --> R[Motor de scoring de riesgo]
    R --> S[Puntuación y nivel de riesgo
(Después)]

    %% Salidas
    F1 --> X1[Exportación XES]
    F2 --> X1
    N  --> X1

    J  --> X2[Recomendaciones JSON]
    H  --> X3[Informes de auditoría]
    K  --> X4[Ranking de trazas]
    S  --> X5[Gráfica Antes vs Después]
```
---

## Descripción detallada del pipeline

### 1. Capa de importación (`gdpr/importers`)

**Propósito**: Normalizar formatos de entrada heterogéneos en una representación interna unificada.

* Formatos soportados:

  * XES (nativo de pm4py)
  * CSV (basado en eventos)
  * JSON (estructura caso–evento)

Todos los formatos se convierten en un **pm4py `EventLog`**, garantizando la compatibilidad con las fases posteriores.

**Abstracción clave:**

* `BaseImporter`
* `load_event_log(path)` dispatcher

---

### 2. Enriquecimiento del contexto GDPR (pipeline principal)

Cada traza se enriquece con atributos relacionados con el RGPD, tales como:

* Presencia de datos personales
* Categoría de datos
* Base legal (por ejemplo, consentimiento)
* Propósito del tratamiento

Este paso establece el contexto de interpretación legal requerido por los validadores.

---

### 3. Construcción de trazas conformes (`pipelines.py`)

A partir de la traza original se construye una línea base conforme al RGPD.
Esta traza representa una ejecución ideal donde:

* El consentimiento precede al acceso
* Los derechos del interesado son respetados
* Se cumplen los plazos legales

Esta línea base actúa como modelo de referencia.

---

### 4. Generación de trazas no conformes (`pipelines.py`, `generators`)

Partiendo de la traza conforme, el sistema introduce violaciones GDPR controladas, como por ejemplo:

* Acceso antes del consentimiento
* Falta de notificación de brechas
* Respuestas tardías a los derechos del interesado
* Respuestas tardías a los derechos del interesado

Pueden inyectarse múltiples violaciones por traza para simular escenarios realistas de no conformidad.

---

### 5. Motor de validación GDPR (`validators.py`)

Cada traza no conforme es analizada por un conjunto de validadores formales, cada uno correspondiente a una obligación del RGPD:

* Licitud del consentimiento
* Plazos de notificación de brechas
* Gestión de los derechos del interesado
* Cumplimiento de restricciones del tratamiento
* Coherencia del borrado de datos

**Output:**

* Lista estructurada de violaciones
* Cada violación incluye:

  * Tipo
  * Severidad
  * Significado legal
  * Eventos causantes

Los eventos infractores se anotan directamente en la traza.

---

### 6. Motor de recomendaciones (`recommendations.py`)

For every detected violation, the system generates:

* A human-readable recommendation
* Severity and risk level
* Legal references (GDPR articles)
* Suggested correct event order or time constraints

Esta capa traduce **violaciones técnicas en orientación accionable.e**.

---

### 7. Scoring de riesgo GDPR (`scoring.py`)

Usando las recomendaciones generadas, se calcula una puntuación cuantitativa de riesgo GDPR por traza.

* Las puntuaciones se basan en la severidad y el nivel de riesgo de las violaciones
* Cada traza se clasifica (por ejemplo, riesgo bajo, medio o alto)

Esto proporciona un indicador compacto de cumplimiento.

---

### 8. Simulación de remediación (`remediation.py`)

El sistema simula la aplicación de las recomendaciones mediante:

* Reordenación de eventos
* Inserción de acciones legalmente requeridas
* Desactivación de accesos ilegales a datos

⚠️ Esto no es una aplicación real de medidas, sino una simulación correctiva hipotética.

---

### 9. Re-validación y análisis post-remediación

La traza remediada es:

1. Re-validada usando los mismos validadores
2. Re-evaluada para calcular el riesgo GDPR tras la remediación

La diferencia entre las puntuaciones antes y después cuantifica la mejora del cumplimiento.

---

### 10. Agregación y analítica

A nivel global, el sistema produce:

* Resumen GDPR global (número y severidad de violaciones)
* Ranking de trazas por riesgo
* Informes de auditoría por traza (narrativa de cumplimiento)
* Visualización del riesgo antes vs después

---

### 11. Capa de exportación (`exporters.py`)

Todos los artefactos se exportan en una carpeta de salida estructurada por log de entrada:

* Logs XES (conforme, no conforme, remediado)
* Informes JSON (recomendaciones, resúmenes, rankings, auditorías)
* Gráficas PNG (comparación de riesgo)

Esto permite reproducibilidad, auditoría y análisis externo.

---
