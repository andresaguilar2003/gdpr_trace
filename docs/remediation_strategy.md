# Remediation Strategy

## Qué Significa “Corrective Simulation” en Este Proyecto

En este proyecto, corrective simulation se refiere a la **modificación controlada de trazas de eventos** con el fin de **estimar el impacto potencial de acciones correctivas alineadas con el GDPR** sobre la conformidad del proceso y los indicadores de riesgo.

La fase de remediación **no** intenta reproducir intervenciones organizativas reales. En su lugar, proporciona un mecanismo analítico de tipo what‑if que permite responder preguntas como:

- **Si las violaciones del GDPR detectadas se abordaran correctamente, cómo cambiaría el estado de cumplimiento**
- **Cuánto se reduciría la puntuación global de riesgo GDPR**
- **Qué tipos de violaciones contribuyen más a la reducción del riesgo cuando se corrigen**

La simulación correctiva opera exclusivamente en el **nivel de abstracción del event‑log**, sin asumir cambios en sistemas reales, procedimientos legales o comportamiento humano.

---

## Qué Significa “Corrective Simulation” en Este Proyecto

El proceso de remediación se aplica **después de la detección de violaciones y la evaluación de riesgo**, y consiste en:

1. Crear una copia profunda de la traza no conforme  
2. Aplicar heurísticas de corrección específicas según la violación 
3. Revalidar la traza corregida
4. Recalcular la puntuación de riesgo GDPR
5. Comparar los niveles de cumplimiento y riesgo antes vs después

Esto permite al sistema producir una **traza contrafactual conforme**, utilizada únicamente para comparación analítica.

---

## Tipos de Correcciones Simuladas

Cada acción correctiva está directamente vinculada a un tipo de violación detectada:

| Violation Type | Simulated Remediation Strategy |
|---------------|--------------------------------|
| Consent after access | Reordenar timestamps para que el consentimiento preceda al acceso |
| Missing consent | Insertar un evento sintético de consentimiento antes del procesamiento |
| Access after withdrawal | Bloquear o deshabilitar accesos después de la retirada |
| Access during restriction | Bloquear accesos durante el intervalo de restricción |
| Late / missing breach notification | Insertar una notificación dentro del plazo legal |
| Missing right response | Insertar un evento de respuesta dentro de los 30 días |
| Implicit consent | Marcar el consentimiento como explícito |
| Purpose limitation violation | Alinear el propósito de acceso con el propósito declarado |
| Data minimization violation | Reducir el alcance de los datos accedidos |
| Access after erasure | Deshabilitar eventos de acceso después del borrado |

Estas estrategias son basadas en reglas y deterministas, diseñadas para alterar mínimamente la traza mientras restauran la validez GDPR.

---

## Qué NO Es la Corrective Simulation

Es esencial distinguir claramente lo que este enfoque de remediación no representa:

- ❌ No es un mecanismo automatizado de aplicación de cumplimiento
- ❌ No representa el comportamiento real de una organización ni procesos legales
- ❌ No garantiza que la traza corregida sea legalmente suficiente en la práctica  
- ❌ No sustituye medidas legales, técnicas u organizativas del GDPR  

Las correcciones simuladas solo demuestran cumplimiento lógico a nivel de orden de eventos, atributos y restricciones.

---

## Valor Científico y Analítico

A pesar de sus limitaciones, la simulación correctiva aporta un fuerte valor analítico:

- Permite comparaciones cuantitativas del riesgo GDPR antes y después de la remediación
- Facilita análisis explicables de mejora del cumplimiento
- Ayuda a identificar categorías de violaciones de alto impacto
- Facilita benchmarking y análisis de sensibilidad

Desde una perspectiva de investigación, este enfoque es comparable al counterfactual reasoning y a las técnicas de process conformance repair utilizadas en la literatura de process mining.

---
