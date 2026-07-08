<div style="height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; border: 4px double #1a3a5a; padding: 20px;">
    <h1 style="font-size: 48px; color: #1a3a5a; margin-bottom: 10px;">GDPR Trace Compliance Rules</h1>
    <h2 style="font-size: 24px; color: #4a6a8a;">Manual de Validación</h2>
    <div style="margin-top: 100px;">
        <p>Versión 1.0 - 2026</p>
    </div>
</div>

<div style="page-break-after: always;"></div>

# Índice

[toc]

<div style="page-break-after: always;"></div>

# GDPR Trace Compliance Rules

## Capítulo II — Principios

### (Artículos 5, 6, 7, 13)

---

### RULE: CASE_START_VERIFY_LEGAL_BASIS

**Objetivo RGPD**

Verificar que existe una base jurídica antes de iniciar el tratamiento de datos personales.

**Artículos RGPD**

* Artículo 5 — Principios del tratamiento
* Artículo 6 — Licitud del tratamiento

<pre class="overflow-visible! px-0!" data-start="742" data-end="999"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv CASE_START_VERIFY_LEGAL_BASIS:</span><br/><span>    for all e in events where e.type = CASE_START:</span><br/><span>        exists g in events such that</span><br/><span>            g.name = verify_legal_basis AND</span><br/><span>            g.position = AFTER AND</span><br/><span>            g.order > e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### RULE: DATA_COLLECTION_NOTICE

**Objetivo RGPD**

Garantizar que el interesado recibe información sobre el tratamiento de datos.

**Artículos RGPD**

* Artículo 13 — Información que deberá facilitarse cuando los datos personales se obtengan del interesado

<pre class="overflow-visible! px-0!" data-start="1272" data-end="1510"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_COLLECTION_NOTICE:</span><br/><span>    for all e where e.type = DATA_COLLECTION:</span><br/><span>        exists g where</span><br/><span>            g.name = privacy_notice_disclosed AND</span><br/><span>            g.position = AFTER AND</span><br/><span>            g.order >= e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### RULE: DATA_COLLECTION_CONSENT_REQUIRED

**Objetivo RGPD**

Garantizar que el consentimiento se verifica cuando constituye la base jurídica del tratamiento.

**Artículos RGPD**

* Artículo 6 — Licitud del tratamiento
* Artículo 7 — Condiciones para el consentimiento

<pre class="overflow-visible! px-0!" data-start="1794" data-end="2015"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_COLLECTION_CONSENT_REQUIRED:</span><br/><span>    if legal_basis = consent:</span><br/><span>        exists g where</span><br/><span>            g.name = check_consent AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### RULE: DATA_COLLECTION_LEGAL_BASIS_FLOW

**Objetivo RGPD**

Asegurar que el tratamiento sólo comienza tras establecer una base legal válida.

**Artículos RGPD**

* Artículo 5 — Principios del tratamiento
* Artículo 6 — Licitud del tratamiento

<pre class="overflow-visible! px-0!" data-start="2660" data-end="2997"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_COLLECTION_LEGAL_BASIS_FLOW:</span><br/><span>    for all e where e.type = DATA_COLLECTION:</span><br/><span>        exists s in events such that</span><br/><span>            s.type = CASE_START AND</span><br/><span>            s.order < e.order</span><br/><span>        and</span><br/><span>        exists g in events such that</span><br/><span>            g.name = 'verify_legal_basis' AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### RULE: DATA_COLLECTION_PURPOSE_REQUIRED

**Objetivo RGPD**

Garantizar la limitación de finalidad y el registro explícito del propósito del tratamiento.

**Artículos RGPD**

* Artículo 5.1.b — Limitación de la finalidad
* Artículo 30 — Registro de actividades de tratamiento

<pre class="overflow-visible! px-0!" data-start="3289" data-end="3457"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_COLLECTION_PURPOSE_REQUIRED:</span><br/><span>    for all e where e.type = DATA_COLLECTION:</span><br/><span>        exists g where</span><br/><span>            g.name = record_purpose</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

# Capítulo III — Derechos del interesado (Artículos 12–23)

## 1. Reglas Generales de Gestión de Solicitudes

*Estas reglas deben cumplirse independientemente del derecho específico que se esté ejerciendo.*

### RULE: USER_RIGHT_IDENTITY_VERIFICATION

**Objetivo RGPD:** Evitar accesos no autorizados verificando la identidad del solicitante.
**Artículos:** Art. 12.2
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_IDENTITY_VERIFICATION:
    for all e where e.type = USER_RIGHT_REQUEST:
        exists g where g.name = verify_request_identity AND g.order < e.order
```

### RULE: USER_RIGHT_REQUEST_RESPONSE_REQUIRED

**Objetivo RGPD:** Garantizar respuesta a solicitudes de ejercicio de derechos.
**Artículos:** Art. 12, 15-18, 21
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_REQUEST_RESPONSE_REQUIRED:
    for all e where e.type = USER_RIGHT_REQUEST:
        exists g where g.name = respond_user_right AND g.order > e.order
```

## 2. Reglas Específicas por Derecho

### A. DERECHO DE ACCESO (Art. 15)

#### RULE: USER_RIGHT_ACCESS_COMPLIANCE

**Objetivo:** Garantizar que las solicitudes de acceso a datos personales sean gestionadas de forma segura y completa, verificando previamente la identidad del solicitante, proporcionando posteriormente una copia de los datos personales tratados y asegurando finalmente una respuesta formal al interesado.
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_ACCESS_DATA_COPY:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = ACCESS:
        exists g where g.name = provide_data_copy AND g.order > e.order
```

## B. DERECHO DE RECTIFICACIÓN (Art. 16)

### RULE: USER_RIGHT_RECTIFICATION_COMPLIANCE

**Objetivo RGPD**

Garantizar que la rectificación solicitada por el interesado se propague correctamente en todos los sistemas relevantes, incluyendo registros principales, réplicas y terceros destinatarios, verificando además la consistencia final de los datos rectificados.

**Artículos RGPD**

* Artículo 16 — Derecho de rectificación
* Artículo 19 — Obligación de notificación relativa a la rectificación

**Object Constraint Language**

<pre class="overflow-visible! px-0!" data-start="532" data-end="1173"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv USER_RIGHT_RECTIFICATION_COMPLIANCE:</span><br/><br/><span>    for all e where</span><br/><span>        e.type = USER_RIGHT_REQUEST and</span><br/><span>        e.user_right_type = RECTIFICATION:</span><br/><br/><span>        exists g1 where</span><br/><span>            g1.name = update_primary_record and</span><br/><span>            g1.order > e.order</span><br/><br/><span>        and exists g2 where</span><br/><span>            g2.name = propagate_rectification_to_replicas and</span><br/><span>            g2.order > e.order</span><br/><br/><span>        and exists g3 where</span><br/><span>            g3.name = notify_data_rectification_to_recipients and</span><br/><span>            g3.order > e.order</span><br/><br/><span>        and exists g4 where</span><br/><span>            g4.name = verify_rectification_consistency and</span><br/><span>            g4.order > e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## C. DERECHO DE SUPRESIÓN / OLVIDO (Art. 17)

### RULE: USER_RIGHT_ERASURE_COMPLIANCE

**Objetivo RGPD**

Garantizar que la supresión de datos personales solicitada por el interesado se ejecute completamente en todos los sistemas afectados, incluyendo registros principales, copias replicadas y terceros destinatarios, verificando posteriormente que la eliminación se ha completado correctamente.

**Artículos RGPD**

* Artículo 17 — Derecho de supresión (“derecho al olvido”)
* Artículo 19 — Obligación de notificación relativa a la supresión

**Object Constraint Language**

<pre class="overflow-visible! px-0!" data-start="1758" data-end="2361"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv USER_RIGHT_ERASURE_COMPLIANCE:</span><br/><br/><span>    for all e where</span><br/><span>        e.type = USER_RIGHT_REQUEST and</span><br/><span>        e.user_right_type = ERASURE:</span><br/><br/><span>        exists g1 where</span><br/><span>            g1.name = erase_primary_record and</span><br/><span>            g1.order > e.order</span><br/><br/><span>        and exists g2 where</span><br/><span>            g2.name = propagate_erasure_to_replicas and</span><br/><span>            g2.order > e.order</span><br/><br/><span>        and exists g3 where</span><br/><span>            g3.name = notify_third_party_deletion and</span><br/><span>            g3.order > e.order</span><br/><br/><span>        and exists g4 where</span><br/><span>            g4.name = verify_erasure_completion and</span><br/><span>            g4.order > e.order</span></code></pre></div></div></div></div></div></div></div></div></div></div></div></div></pre>

### D. DERECHO A LA LIMITACIÓN (Art. 18)

#### RULE: USER_RIGHT_RESTRICTION_COMPLIANCE

**Objetivo:** Garantizar que, ante una solicitud de limitación del tratamiento, se verifiquen previamente las condiciones legales necesarias antes de levantar o modificar la restricción, se aplique posteriormente el marcado de restricción sobre los datos afectados y finalmente se proporcione una respuesta formal al interesado.

**Artículos RGPD**

* Artículo 18 — Derecho a la limitación del tratamiento
* Artículo 12 — Obligación de respuesta al interesado

**Object Constraint Language**

<pre class="overflow-visible! px-0!" data-start="5064" data-end="5673"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv USER_RIGHT_RESTRICTION_COMPLIANCE:</span><br/><br/><span>    for all e where</span><br/><span>        e.type = USER_RIGHT_REQUEST and</span><br/><span>        e.user_right_type = RESTRICTION:</span><br/><br/><span>        exists g0 where</span><br/><span>            g0.name = verify_request_identity and</span><br/><span>            g0.order < e.order</span><br/><br/><span>        and exists g1 where</span><br/><span>            g1.name = verify_restriction_lift_conditions and</span><br/><span>            g1.order < e.order</span><br/><br/><span>        and exists g2 where</span><br/><span>            g2.name = mark_data_as_restricted and</span><br/><span>            g2.order > e.order</span><br/><br/><span>        and exists g3 where</span><br/><span>            g3.name = respond_user_right and</span><br/><span>            g3.order > g2.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

### E. DERECHO A LA PORTABILIDAD (Art. 20)

#### RULE: USER_RIGHT_PORTABILITY_FORMAT

**Objetivo:** Generar datos en formato interoperable y lectura mecánica.
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_PORTABILITY_FORMAT:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:
        exists g where g.name = generate_interoperable_format AND g.order > e.order
```

### RULE: USER_RIGHT_PORTABILITY_TRANSMISSION

**Objetivo:** Garantizar que, cuando sea técnicamente posible, los datos se transmitan directamente de responsable a responsable a solicitud del interesado.
**Artículos:** Artículo 20.2
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_PORTABILITY_TRANSMISSION:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = PORTABILITY:
        exists g where g.name = transmit_data_to_new_controller AND g.order > e.order
```

### F. DERECHO DE OPOSICIÓN (Art. 21)

#### RULE: USER_RIGHT_OBJECTION_HALT

**Objetivo:** Cese inmediato del tratamiento tras la oposición.
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_OBJECTION_HALT:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:
        exists g where g.name = halt_processing_activities AND g.order > e.order
```

#### RULE: USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION

**Objetivo:** Verificar si existen motivos legítimos imperiosos que prevalezcan sobre los intereses del interesado antes de denegar o aceptar una oposición.
**Artículos:** Artículo 21.1
**OCL:**

**Object Constraint Language**

```
context Trace
inv USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = OBJECTION:
        exists g where g.name = verify_compelling_legitimate_grounds AND g.position = BEFORE
```

### G. DECISIONES AUTOMATIZADAS (Art. 22)

#### RULE: USER_RIGHT_AUTOMATED_DECISION_CONTEST

**Objetivo:** Garantizar que el interesado pueda impugnar una decisión basada únicamente en el tratamiento automatizado y obtener intervención humana.

**Artículos RGPD:**

* Artículo 22.3 — Derecho a obtener intervención humana, a expresar su punto de vista y a impugnar la decisión.

**Object Constraint Language**

```
context Trace

inv USER_RIGHT_AUTOMATED_DECISION_CONTEST:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = AUTOMATED_DECISION_REVIEW:
        exists g where 
            g.name = contest_automated_decision AND 
            g.order > e.order
```

### H. INFORMACIÓN (Art. 23)

#### RULE: USER_RIGHT_INFORMATION_TRANSPARENCY

**Objetivo RGPD**

Asegurar que se facilite al interesado la información detallada sobre el tratamiento (identidad del responsable, fines, base jurídica) cuando se solicita bajo el derecho de información.

**Artículos RGPD**

* Artículo 13 — Información que deberá facilitarse cuando los datos se obtengan del interesado
* Artículo 14 — Información que deberá facilitarse cuando los datos no se hayan obtenido del interesado

**Object Constraint Language**

```
context Trace

inv USER_RIGHT_INFORMATION_TRANSPARENCY:
    for all e where e.type = USER_RIGHT_REQUEST and e.user_right_type = INFORMATION:
        exists g where
            g.name = provide_transparency_details AND
            g.position = AFTER AND
            g.order > e.order
```

# Capítulo IV — Responsable y encargado del tratamiento

### (Artículos 24–43)

---

## RULE: DATA_PROCESSING_MINIMISATION

**Objetivo RGPD**

Garantizar la minimización de datos durante el tratamiento.

**Artículos RGPD**

* Artículo 5.1.c — Minimización de datos
* Artículo 25 — Protección de datos desde el diseño

<pre class="overflow-visible! px-0!" data-start="4491" data-end="4729"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_PROCESSING_MINIMISATION:</span><br/><span>    for all e where e.type = DATA_PROCESSING:</span><br/><span>        exists g where</span><br/><span>            g.name = minimisation_check AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: DATA_PROCESSING_ENCRYPTION_REQUIRED

**Objetivo RGPD**

Garantizar medidas de seguridad apropiadas para categorías sensibles de datos.

**Artículos RGPD**

* Artículo 32 — Seguridad del tratamiento

<pre class="overflow-visible! px-0!" data-start="4951" data-end="5184"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_PROCESSING_ENCRYPTION_REQUIRED:</span><br/><span>    if data_category != STANDARD:</span><br/><span>        exists g where</span><br/><span>            g.name = encryption_applied AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---


## RULE: DATA_PROCESSING_LOG_REQUIRED

**Objetivo RGPD**

Garantizar trazabilidad y accountability sobre actividades de tratamiento.

**Artículos RGPD**

* Artículo 5.2 — Responsabilidad proactiva
* Artículo 30 — Registro de actividades de tratamiento

<pre class="overflow-visible! px-0!" data-start="5845" data-end="6131"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_PROCESSING_LOG_REQUIRED:</span><br/><span>    for all e where e.type = DATA_PROCESSING:</span><br/><span>        exists g where</span><br/><span>            g.name = log_processing_activity</span><br/><span>        OR</span><br/><span>        exists g where</span><br/><span>            g.name = log_processing_activity AND</span><br/><span>            g.order > e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: DATA_ACCESS_CONTROL_REQUIRED

**Objetivo RGPD**

Garantizar controles de acceso para datos sensibles.

**Artículos RGPD**

* Artículo 32 — Seguridad del tratamiento
* Artículo 9 — Categorías especiales de datos

<pre class="overflow-visible! px-0!" data-start="6366" data-end="6603"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_ACCESS_CONTROL_REQUIRED:</span><br/><span>    if data_category in {HEALTH, SPECIAL}:</span><br/><span>        exists g where</span><br/><span>            g.name = access_control_check AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: DATA_TRANSFER_THIRD_PARTY_REQUIRED

**Objetivo RGPD**

Garantizar acuerdos con terceros receptores de datos.

**Artículos RGPD**

* Artículo 28 — Encargado del tratamiento

<pre class="overflow-visible! px-0!" data-start="7156" data-end="7405"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_TRANSFER_THIRD_PARTY_REQUIRED:</span><br/><span>    if has_third_party_recipients = true:</span><br/><span>        exists g where</span><br/><span>            g.name = check_third_party_agreement AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

---

## RULE: AUTOMATED_DECISION_DISCLOSURE_REQUIRED

**Objetivo RGPD**

Garantizar transparencia en decisiones automatizadas.

**Artículos RGPD**

* Artículo 22 — Decisiones automatizadas
* Artículo 13.2.f — Información sobre lógica aplicada

<pre class="overflow-visible! px-0!" data-start="8048" data-end="8307"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv AUTOMATED_DECISION_DISCLOSURE_REQUIRED:</span><br/><span>    for all e where e.type = AUTOMATED_DECISION:</span><br/><span>        exists g where</span><br/><span>            g.name = automated_logic_disclosure AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

# Capítulo V — Transferencias internacionales

### (Artículos 44–50)

---

## RULE: DATA_TRANSFER_INTERNATIONAL_REQUIRED

**Objetivo RGPD**

Garantizar salvaguardas adecuadas en transferencias internacionales.

**Artículos RGPD**

* Artículo 44 — Principio general
* Artículo 46 — Garantías adecuadas

<pre class="overflow-visible! px-0!" data-start="8622" data-end="8883"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_TRANSFER_INTERNATIONAL_REQUIRED:</span><br/><span>    if international_transfer = "third_country":</span><br/><span>        exists g where</span><br/><span>            g.name = verify_international_safeguard AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

# Capítulo IV — Seguridad y ciclo de vida del dato

### (Artículos 5, 17, 25, 32)

---

## RULE: DATA_DELETION_RETENTION_REQUIRED

**Objetivo RGPD**

Garantizar control previo del periodo de conservación antes del borrado.

**Artículos RGPD**

* Artículo 5.1.e — Limitación del plazo de conservación

<pre class="overflow-visible! px-0!" data-start="9617" data-end="9829"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_DELETION_RETENTION_REQUIRED:</span><br/><span>    for all e where e.type = DATA_DELETION:</span><br/><span>        exists g1 where</span><br/><span>            g1.name = record_retention_period AND</span><br/><span>            g1.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: DATA_DELETION_ERASE_REQUIRED

**Objetivo RGPD**

Garantizar ejecución efectiva de la supresión de datos.

**Artículos RGPD**

* Artículo 17 — Derecho de supresión

<pre class="overflow-visible! px-0!" data-start="10016" data-end="10209"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_DELETION_ERASE_REQUIRED:</span><br/><span>    for all e where e.type = DATA_DELETION:</span><br/><span>        exists g3 where</span><br/><span>            g.name = erase_data AND</span><br/><span>            g.order > e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: CASE_END_RETENTION_VERIFY

**Objetivo RGPD**

Verificar el cumplimiento de la política de conservación al finalizar el caso.

**Artículos RGPD**

* Artículo 5.1.e — Conservación limitada

<pre class="overflow-visible! px-0!" data-start="10420" data-end="10679"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv CASE_END_RETENTION_VERIFY:</span><br/><span>    for all e in events where e.type = CASE_END:</span><br/><span>        exists g in events such that</span><br/><span>            g.name = 'retention_period_verify' AND</span><br/><span>            g.position = BEFORE AND</span><br/><span>            g.order < e.order</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## RULE: CASE_END_ERASURE

**Objetivo RGPD**

Garantizar eliminación de datos cuando termina el periodo de retención.

**Artículos RGPD**

* Artículo 17 — Derecho de supresión
* Artículo 25 — Protección de datos desde el diseño

<pre class="overflow-visible! px-0!" data-start="10922" data-end="11291"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv CASE_END_ERASURE:</span><br/><span>    for all e in events where e.type = CASE_END:</span><br/><span>        if not context.retention_period.oclIsUndefined() then</span><br/><span>            exists g in events such that</span><br/><span>                g.name = 'confirm_data_erasure' AND</span><br/><span>                g.position = BEFORE AND</span><br/><span>                g.order < e.order</span><br/><span>        else</span><br/><span>            true</span><br/><span>        endif</span></code></pre></div></div></div></div></div></div></div></div></div></div></div></div></pre>

# Warnings & Señales de Cumplimiento No Críticas

## Propósito

Las siguientes reglas están clasificadas como **advertencias** en lugar de violaciones estrictas del RGPD.

Estas situaciones no indican necesariamente un tratamiento de datos ilícito.

En su lugar, representan:

* controles innecesarios del RGPD,
* exceso de cumplimiento (sobrecumplimiento),
* salvaguardas redundantes,
* o prácticas de gobernanza ineficientes.

Las advertencias deben interpretarse como recomendaciones de optimización o coherencia, más que como fallos de cumplimiento.

---

### WARNING: DATA_COLLECTION_CONSENT_FORBIDDEN

**Objetivo RGPD**

Evitar verificaciones innecesarias de consentimiento cuando la base jurídica no es el consentimiento.

**Artículos RGPD**

* Artículo 6 — Licitud del tratamiento

<pre class="overflow-visible! px-0!" data-start="2255" data-end="2400"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_COLLECTION_CONSENT_FORBIDDEN:</span><br/><span>    if legal_basis != consent:</span><br/><span>        not exists g where g.name = check_consent</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### WARNING: DATA_PROCESSING_ENCRYPTION_FORBIDDEN

**Objetivo RGPD**

Evitar enriquecimientos innecesarios cuando no son requeridos por el nivel de riesgo definido.

**Artículos RGPD**

* Artículo 32 — Seguridad del tratamiento

<pre class="overflow-visible! px-0!" data-start="5423" data-end="5578"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_PROCESSING_ENCRYPTION_FORBIDDEN:</span><br/><span>    if data_category = STANDARD:</span><br/><span>        not exists g where g.name = encryption_applied</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### WARNING: DATA_ACCESS_CONTROL_FORBIDDEN

**Objetivo RGPD**

Evitar controles innecesarios para categorías estándar.

**Artículos RGPD**

* Artículo 32 — Seguridad del tratamiento

<pre class="overflow-visible! px-0!" data-start="6796" data-end="6960"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_ACCESS_CONTROL_FORBIDDEN:</span><br/><span>    if data_category not in {HEALTH, SPECIAL}:</span><br/><span>        not exists g where g.name = access_control_check</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

### WARNING: DATA_TRANSFER_THIRD_PARTY_FORBIDDEN

**Objetivo RGPD**

Evitar verificaciones innecesarias cuando no existen terceros receptores.

**Artículos RGPD**

* Artículo 28 — Encargado del tratamiento

<pre class="overflow-visible! px-0!" data-start="7622" data-end="7795"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_TRANSFER_THIRD_PARTY_FORBIDDEN:</span><br/><span>    if has_third_party_recipients = false:</span><br/><span>        not exists g where g.name = check_third_party_agreement</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

### WARNING: DATA_TRANSFER_INTERNATIONAL_FORBIDDEN

**Objetivo RGPD**

Evitar verificaciones innecesarias cuando no existen transferencias internacionales.

**Artículos RGPD**

* Artículo 44 — Transferencias internacionales

<pre class="overflow-visible! px-0!" data-start="9118" data-end="9303"><div class="relative w-full mt-4 mb-1"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border border-token-border-light border-radius-3xl corner-superellipse/1.1 rounded-3xl"><div class="h-full w-full border-radius-3xl bg-token-bg-elevated-secondary corner-superellipse/1.1 overflow-clip rounded-3xl lxnfua_clipPathFallback"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="relative"><div class=""><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼd ͼr"><div class="cm-scroller"><pre class="cm-content q9tKkq_readonly m-0"><code><span>context Trace</span><br/><br/><span>inv DATA_TRANSFER_INTERNATIONAL_FORBIDDEN:</span><br/><span>    if international_transfer != "third_country":</span><br/><span>        not exists g where g.name = verify_international_safeguard</span></code></pre></div></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

```

```
