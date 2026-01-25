# GDPR Model

Este documento describe el **modelo GDPR implementado en el proyecto**, detallando:

* Qué **eventos GDPR** se modelan
* Cómo se relacionan con el **flujo del sistema**
* Qué **artículos del RGPD** justifican cada evento
* Qué **suposiciones de modelado** se han adoptado

El objetivo es dejar claro que el sistema no introduce eventos arbitrarios, sino que sigue un **modelo explícito, trazable y legalmente fundamentado**.

---

## 1. Principios de modelado

El proyecto modela el RGPD como un **sistema orientado a eventos**, donde:

* Cada obligación legal relevante se representa como un **evento explícito en la traza**.
* Los eventos GDPR se insertan, validan o eliminan **sin modificar la semántica del proceso original**, solo su envoltura legal.
* El análisis se realiza **a nivel de traza**, no de log agregado, permitiendo auditoría individual.

Se distinguen dos tipos de eventos:

* **Eventos del proceso real** (clínicos, administrativos, técnicos)
* **Eventos GDPR**, identificados por `gdpr:event = True`

---

## 2. Inicio del tratamiento y consentimiento

### Eventos

| Evento             | Descripción                               |
| ------------------ | ----------------------------------------- |
| `gdpr:sendData`    | Inicio potencial del tratamiento de datos |
| `gdpr:informUser`  | Información al interesado                 |
| `gdpr:giveConsent` | Consentimiento explícito                  |

### Flujo modelado

```
sendData → informUser → giveConsent → (proceso principal)
```

### Justificación legal

* **Art. 5(1)(a)** — Licitud, lealtad y transparencia
* **Art. 6(1)(a)** — Licitud basada en consentimiento
* **Art. 7** — Condiciones para el consentimiento
* **Art. 13** — Información al interesado

### Suposiciones

* El consentimiento es **explícito**, no implícito
* El consentimiento debe ocurrir **antes de cualquier acceso a datos personales**
* El consentimiento tiene un **alcance (`gdpr:scope`) y propósito**

---

## 3. Expiración y retirada del consentimiento

### Eventos

| Evento                 | Descripción                              |
| ---------------------- | ---------------------------------------- |
| `gdpr:consentExpired`  | Expiración automática del consentimiento |
| `gdpr:withdrawConsent` | Retirada explícita del consentimiento    |

### Justificación legal

* **Art. 7(3)** — Derecho a retirar el consentimiento
* **Art. 5(1)(e)** — Limitación del plazo de conservación

### Regla de validación

> Cualquier acceso a datos tras la expiración o retirada del consentimiento constituye una violación.

---

## 4. Acceso a datos y control de autorizaciones

### Eventos

| Evento                     | Descripción                   |
| -------------------------- | ----------------------------- |
| `gdpr:permissionGranted`   | Autorización previa al acceso |
| `gdpr:accessLog`           | Registro del acceso           |
| `gdpr:updateAccessHistory` | Persistencia del historial    |

### Tipos de acceso

* `gdpr:read`
* `gdpr:write`

### Justificación legal

* **Art. 5(2)** — Responsabilidad proactiva (*accountability*)
* **Art. 24** — Responsabilidad del responsable
* **Art. 32** — Seguridad del tratamiento

### Suposiciones

* Todo acceso válido debe estar precedido por una autorización explícita
* Todo acceso autorizado debe dejar traza

---

## 5. Restricción del tratamiento

### Eventos

| Evento                    | Descripción                     |
| ------------------------- | ------------------------------- |
| `gdpr:restrictProcessing` | Restricción del tratamiento     |
| `gdpr:liftRestriction`    | Levantamiento de la restricción |

### Justificación legal

* **Art. 18** — Derecho a la limitación del tratamiento

### Regla

> Durante una restricción activa, ningún acceso a datos personales está permitido.

---

## 6. Derecho de supresión (derecho al olvido)

### Eventos

| Evento                    | Descripción           |
| ------------------------- | --------------------- |
| `gdpr:removeDataRequest`  | Solicitud de borrado  |
| `gdpr:searchDataLocation` | Localización de datos |
| `gdpr:eraseData`          | Borrado efectivo      |

### Justificación legal

* **Art. 17** — Derecho de supresión

### Restricciones temporales

* El borrado debe producirse dentro de un **plazo legal máximo**
* Cualquier acceso posterior al borrado es una violación grave

---

## 7. Derecho de rectificación

### Evento

| Evento             | Descripción            |
| ------------------ | ---------------------- |
| `gdpr:rectifyData` | Rectificación de datos |

### Justificación legal

* **Art. 16** — Derecho de rectificación

---

## 8. Brechas de seguridad

### Eventos

| Evento              | Descripción            |
| ------------------- | ---------------------- |
| `gdpr:detectBreach` | Detección de brecha    |
| `gdpr:notifyBreach` | Notificación de brecha |

### Justificación legal

* **Art. 33** — Notificación a la autoridad (≤ 72h)
* **Art. 34** — Comunicación al interesado

### Regla

> La notificación fuera de 72h constituye una violación GDPR.

---

## 9. Derechos de acceso e información

### Eventos

| Evento             | Descripción               |
| ------------------ | ------------------------- |
| `gdpr:requestInfo` | Solicitud de información  |
| `gdpr:provideInfo` | Respuesta del responsable |

### Justificación legal

* **Art. 12** — Transparencia y plazos
* **Art. 15** — Derecho de acceso

### Restricción temporal

* Respuesta ≤ **30 días**

---

## 10. Violaciones modeladas explícitamente

El sistema puede generar, detectar y remediar, entre otras:

* Consentimiento ausente o tardío
* Acceso sin base legal
* Acceso durante restricción
* Acceso tras borrado
* Notificación tardía de brechas
* Incumplimiento de derechos del interesado

Estas violaciones alimentan:

* Validadores GDPR
* Sistema de recomendaciones
* Cálculo del GDPR Risk Score

---
