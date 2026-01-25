# GDPR Validation Rules

Este documento describe las **reglas de validación GDPR** implementadas en el sistema, su correspondencia con los artículos del **Reglamento General de Protección de Datos (RGPD)** y el impacto legal de cada incumplimiento detectado.

Cada regla se aplica a **nivel de traza individual** y analiza la **secuencia temporal y semántica** de eventos enriquecidos con información GDPR.

---

## Tabla resumen de validadores

| Validator | Artículo GDPR | Severidad | Descripción |
|---------|---------------|-----------|-------------|
| `validate_consent_before_access` | Art. 6, Art. 7 | High | Detecta accesos a datos personales realizados sin consentimiento previo o con consentimiento obtenido después del acceso. |
| `validate_withdrawn_consent` | Art. 7.3 | High | Identifica accesos a datos personales tras la retirada explícita del consentimiento por parte del interesado. |
| `validate_processing_restriction` | Art. 18 | High | Comprueba que no se realicen accesos a datos mientras el tratamiento está restringido. |
| `validate_breach_notification_time` | Art. 33 | Critical | Verifica que las brechas de seguridad sean notificadas y dentro del plazo legal máximo de 72 horas. |
| `validate_data_subject_rights` | Art. 12, Art. 15 | Medium | Detecta solicitudes de derechos del interesado sin respuesta o respondidas fuera del plazo legal de 30 días. |
| `validate_erase_without_processing` | Art. 5(1)(a) | Low | Señala incoherencias cuando se solicita el borrado sin que exista constancia de tratamiento previo. |
| `validate_implicit_consent` | Art. 4(11), Art. 7 | Medium | Detecta consentimientos que no cumplen el requisito de ser explícitos. |
| `validate_purpose_limitation` | Art. 5(1)(b) | High | Identifica accesos a datos con un propósito distinto al declarado y autorizado. |
| `validate_data_minimization` | Art. 5(1)(c) | Medium | Detecta accesos a un volumen o alcance de datos superior al estrictamente necesario. |
| `validate_access_after_erasure` | Art. 17 | Critical | Detecta accesos a datos personales después de haberse ejecutado una solicitud de borrado. |

---

## Descripción detallada de las reglas

### 1. Consentimiento previo al acceso

**Validator:** `validate_consent_before_access`  
**Artículos:** Art. 6 (Licitud), Art. 7 (Condiciones del consentimiento)

Esta regla garantiza que todo acceso a datos personales esté precedido por un evento de consentimiento válido.

Se contemplan dos escenarios de incumplimiento:

- Accesos sin ningún consentimiento registrado.
- Accesos cuya marca temporal es anterior al consentimiento.

---

### 2. Retirada del consentimiento

**Validator:** `validate_withdrawn_consent`  
**Artículo:** Art. 7.3

Una vez retirado el consentimiento, el responsable debe cesar inmediatamente cualquier tratamiento.

La regla detecta cualquier evento de acceso posterior a un evento `withdraw`.

---

### 3. Restricción del tratamiento

**Validator:** `validate_processing_restriction`  
**Artículo:** Art. 18

Durante un periodo de restricción, el tratamiento debe quedar bloqueado.

Esta validación comprueba que no existan accesos entre los eventos `restrictProcessing` y `liftRestriction`.

---

### 4. Notificación de brechas de seguridad

**Validator:** `validate_breach_notification_time`  
**Artículo:** Art. 33

Este validador controla dos incumplimientos críticos:

- Ausencia total de notificación tras detectar una brecha.
- Notificación realizada fuera del plazo máximo de 72 horas.

---

### 5. Derechos del interesado

**Validator:** `validate_data_subject_rights`  
**Artículos:** Art. 12, Art. 15

Verifica que toda solicitud de información (`requestInfo`) tenga una respuesta (`provideInfo`) y que esta se produzca dentro de los **30 días legales**.

---

### 6. Borrado sin tratamiento previo

**Validator:** `validate_erase_without_processing`  
**Artículo:** Art. 5(1)(a)

Detecta inconsistencias de proceso cuando se solicita el borrado de datos sin que exista evidencia de acceso o tratamiento previo.

---

### 7. Consentimiento implícito

**Validator:** `validate_implicit_consent`  
**Artículos:** Art. 4(11), Art. 7

El RGPD exige consentimiento **libre, específico, informado e inequívoco**.

Este validador detecta eventos de consentimiento que no estén marcados como explícitos.

---

### 8. Limitación de la finalidad

**Validator:** `validate_purpose_limitation`  
**Artículo:** Art. 5(1)(b)

Comprueba que los accesos a datos se realicen únicamente para el propósito declarado en la traza (`gdpr:default_purpose`).

---

### 9. Minimización de datos

**Validator:** `validate_data_minimization`  
**Artículo:** Art. 5(1)(c)

Detecta accesos donde el alcance de los datos (`gdpr:data_scope`) excede lo necesario para el propósito legítimo.

---

### 10. Acceso tras el borrado

**Validator:** `validate_access_after_erasure`  
**Artículo:** Art. 17

Cualquier acceso posterior a un evento de borrado constituye una violación grave del **derecho al olvido** y se marca como crítica.
