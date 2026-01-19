# Limitaciones del Enfoque

Esta sección describe las principales **limitaciones técnicas, conceptuales y legales** del sistema propuesto. Reconocer explícitamente estas limitaciones es esencial para garantizar el rigor académico y una correcta interpretación de los resultados.

---

## 1. Abstracción a Nivel de Log de Eventos

El sistema opera exclusivamente sobre **registros de eventos** y sus atributos.

- No existe acceso a bases de datos reales, aplicaciones o infraestructuras
- No se verifica el flujo real de datos ni sus ubicaciones de almacenamiento
- No hay garantía de que los eventos registrados representen completamente la realidad

Como resultado, el cumplimiento se evalúa **únicamente a nivel de comportamiento registrado**, no sobre el tratamiento real de los datos.

---

## 2. Semántica GDPR Sintética y Asumida

Los eventos relacionados con el RGPD (por ejemplo, consentimiento, restricción, borrado) son:

- Generados de forma sintética
- O inferidos mediante reglas de enriquecimiento del log

Esto implica que:
- La corrección de la validación depende de la calidad de la anotación de los eventos
- Anotaciones incompletas o incorrectas pueden dar lugar a falsos positivos o falsos negativos

---

## 3. Interpretación Legal Simplificada

El proyecto adopta una **interpretación simplificada y operativa** de las normas del RGPD:

- No se modelan excepciones legales (por ejemplo, interés legítimo u obligación legal)
- Se ignoran interpretaciones dependientes del contexto por parte de las autoridades de control
- No se tienen en cuenta variaciones jurisdiccionales

Por tanto, las violaciones detectadas deben interpretarse como **riesgos potenciales**, no como infracciones legales definitivas.

---

## 4. Reglas de Validación Deterministas

Todos los validadores están implementados como **comprobaciones deterministas basadas en reglas**:

- No se emplea razonamiento probabilístico
- No se modela la incertidumbre
- No se aprende a partir de decisiones históricas de cumplimiento

Esto limita la adaptabilidad del sistema a escenarios reales complejos o ambiguos.

---

## 5. La Simulación Correctiva No es una Remediación Real

Tal como se detalla en `remediation_strategy.md`, las correcciones simuladas:

- No representan acciones correctivas reales
- No tienen en cuenta restricciones organizativas
- No modelan retrasos legales, técnicos o humanos

Sirven exclusivamente para **análisis contrafactual**, no como guía operativa.

---

## 6. Cobertura Limitada de Artículos del RGPD

Aunque el proyecto cubre varios principios fundamentales del RGPD, **no aborda**:

- Evaluaciones de impacto en la protección de datos (Art. 35)
- Registros de actividades de tratamiento (Art. 30)
- Transferencias internacionales de datos (Capítulo V)
- Protección de datos desde el diseño y por defecto (Art. 25)
- Implementación de medidas de seguridad (Art. 32)

Por ello, el sistema no debe considerarse una solución completa de cumplimiento del RGPD.

---

## 7. Ausencia de Modelado Causal u Organizativo

El sistema no modela:

- La toma de decisiones humanas
- Las responsabilidades organizativas
- Las arquitecturas técnicas de los sistemas
- La aplicación de sanciones o mecanismos de enforcement

Todo el análisis es **conductual y retrospectivo**, no causal.

---

## 8. Escalabilidad y Rendimiento

La implementación no ha sido optimizada para:

- Logs de eventos de muy gran tamaño
- Monitorización de cumplimiento en tiempo real
- Entornos distribuidos

Por tanto, los resultados de rendimiento no deben extrapolarse a sistemas en producción.

---

## Observación Final

El sistema debe entenderse como:

> **Un marco orientado a la investigación para analizar patrones de cumplimiento del RGPD en registros de eventos, no como una herramienta de evaluación de cumplimiento legalmente vinculante.**

Estas limitaciones no debilitan la contribución; al contrario, delimitan claramente su alcance y garantizan una interpretación responsable de los resultados.
