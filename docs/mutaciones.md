# Sistema de Inyección de Mutaciones y Validación RGPD en Event Logs (.XES)

## 1. Introducción y Flujo del Sistema

El propósito principal de esta aplicación es la auditoría y validación del cumplimiento del Reglamento General de Protección de Datos (RGPD) sobre procesos de negocio representados en formato `.xes` (eXtensible Event Stream). El ciclo de vida de los datos dentro del sistema se compone de tres fases secuenciales:

1. **Importación y Tipado:** Se lee el conjunto de datos original. Cada evento nativo del *dataset* se asocia a un tipo de actividad genérica (ej. `DATA_COLLECTION`).
2. **Enriquecimiento del Contexto:** El *dataset* es dotado de un contexto global (atributos como `legal_basis`, `purpose`, `data_category`). Utilizando este contexto y las reglas operacionales basadas en la ley, el sistema inyecta **eventos RGPD obligatorios** (ej. `check_consent`, `privacy_notice_disclosed`, `verify_legal_basis`) en posiciones relativas específicas (`BEFORE` o `AFTER`) respecto a los eventos originales de la traza.
3. **Inyección de Mutaciones (Generación de Fallos):** Una vez validada la traza enriquecida ideal, el sistema introduce deliberadamente  **mutaciones** . Estas mutaciones representan de forma sintética violaciones o advertencias operacionales ( *warnings* ) respecto al cumplimiento normativo. Su objetivo es evaluar la robustez de los componentes de auditoría y servir como base para el entrenamiento de modelos predictivos.

## 2. Tipología de Mutaciones

Las mutaciones se clasifican en cuatro categorías fundamentales según la naturaleza de la alteración que provocan en el flujo de procesos:

### 2.1. Mutaciones Estructurales

Se centran en la manipulación directa de la existencia de los eventos dentro de la secuencia. No alteran los atributos internos ni el contexto, sino la estructura lineal de la traza.

* **Operaciones comunes:** Eliminar un evento crítico, duplicar registros o alterar su orden posicional arbitrariamente.
* **Impacto:** Provoca la ausencia de evidencias de cumplimiento exigidas por la normativa.

### 2.2. Mutaciones Temporales

Alteran la dimensión cronológica y secuencial de los eventos. Cada evento de cumplimiento RGPD posee una propiedad posicional intrínseca (`BEFORE` o `AFTER`) que determina su validez respecto al evento operativo del negocio.

* **Operaciones comunes:** Intercambiar el identificador de orden (`order`) o modificar las marcas de tiempo ( *timestamps* ).
* **Impacto:** Genera anacronismos legales (por ejemplo, verificar el consentimiento del usuario *después* de haber recolectado y almacenado sus datos protegidos).

### 2.3. Mutaciones Contextuales

Involucran la desconexión o incongruencia entre los parámetros del entorno normativo global del proceso y los eventos inyectados en las trazas.

* **Operaciones comunes:** Modificar o eliminar el valor de un atributo del contexto (ej. cambiar `legal_basis` de `"consent"` a `"contract"`), o eliminar un evento RGPD que es estrictamente vinculante debido a la configuración actual de dicho contexto.
* **Impacto:** Si la base legal se altera o si el evento asociado (como `check_consent`) desaparece estando la base configurada bajo consentimiento, se incurre en un procesamiento ilícito de datos según el Art. 7 del RGPD.

### 2.4. Mutaciones Semánticas

Representan casos complejos aplicados a bloques o dependencias lógicas rígidas entre flujos de control. No se evalúan de forma aislada, sino bajo la premisa de cadenas de cumplimiento que deben mantenerse indivisibles.

* **Operaciones comunes:** Ruptura de secuencias iniciales de verificación obligatoria.
* **Impacto:** Si un evento de tipo `DATA_COLLECTION` ocurre en cualquier punto del proceso, semánticamente se exige que en el inicio de la traza (`CASE_START`) se haya ejecutado con éxito la validación de la base jurídica (`verify_legal_basis`). Eliminar o desplazar este evento inicial corrompe la semántica de licitud del proceso completo.

## 3. Arquitectura de Validación

Para detectar y clasificar tanto las trazas conformes como aquellas que han sufrido alteraciones a través de las mutaciones, el sistema implementa una estrategia de validación dual:

### 3.1. Validador Determinista (Reglas Basadas en Código / OCL)

Programado en Python nativo, actúa como un motor de reglas estricto que evalúa de forma algorítmica las restricciones posicionales, temporales y de contexto.

Como ejemplo del motor determinista, las reglas aplicadas al bloque de **Recolección de Datos (`DATA_COLLECTION`)** evalúan de forma estricta los siguientes criterios lógicos:

* **Existencia Global de Transparencia:** Se exige de forma obligatoria la presencia de la notificación de privacidad (`privacy_notice_disclosed`). Su ausencia genera una violación directa al Artículo 13 del RGPD.
* **Validación de la Base Legal:** Si el contexto define que la base jurídica es el consentimiento (`"consent"`), la ausencia del evento `check_consent` se tipifica como violación (Art. 7). Si se encuentra presente pero el contexto indica otra base de procesamiento, se emite un *warning* por procesamiento innecesario de datos (Principios de minimización Art. 5/25).
* **Consistencia Cronológica (Ordenación):** Verifica mediante operadores lógicos que `privacy_notice_disclosed` ocurra en un índice de orden posterior o igual (`>=`) al de la recolección, y que `check_consent` preceda estrictamente (`<`) a la captura de los datos.
* **Flujo Semántico Inicial:** Asegura que los bloques iniciales `CASE_START` junto con `verify_legal_basis` se hayan ejecutado cronológicamente antes de realizar cualquier llamada a actividades de recolección de datos protegidos.

### 3.2. Validador No Determinista (Inteligencia Artificial)

Componente actualmente bajo fase de investigación y desarrollo (R&D). Su objetivo es delegar la auditoría del cumplimiento normativo a un modelo de lenguaje y aprendizaje profundo capaz de identificar patrones de violación semántica y temporal complejos que escapan a las reglas cableadas en código.

* **Modelo Evaluado:** Se está experimentando con la arquitectura **T5-small** ( *Text-to-Text Transfer Transformer* ), alimentando al modelo con representaciones textuales o estructuradas de las secuencias de eventos para que aprenda a predecir la conformidad o a clasificar el tipo de mutación/infracción inyectada en el flujo.

## 4. Catálogo de Operadores de Mutación

Este apartado describe el conjunto de mutaciones sintéticas implementadas en la aplicación. Cada operador actúa como un inyector de fallos diseñado para simular malas prácticas operacionales o evasiones intencionadas del RGPD.

### 4.1. Mutaciones Estructurales (`MutationCategory.STRUCTURAL`)

Estas mutaciones alteran directamente la presencia o la composición física de los eventos RGPD en la traza sin modificar las variables del contexto circundante.

* `remove_verify_legal_basis`:
  * **Clase asociada:** `RemoveEventMutation("verify_legal_basis")`
  * **Propósito:** Elimina el evento obligatorio de verificación de base jurídica. Provoca la ausencia de evidencias sobre la licitud del tratamiento al inicio del proceso.
* `duplicate_verify_legal_basis`:
  * **Clase asociada:** `DuplicateEventMutation("verify_legal_basis")`
  * **Propósito:** Clona el evento de verificación de la base jurídica en la traza. Se utiliza para evaluar si el validador detecta redundancias ineficientes o ruido en el registro de auditoría.
* `remove_check_consent`:
  * **Clase asociada:** `RemoveEventMutation("check_consent")`
  * **Propósito:** Remueve la verificación del consentimiento. Si el contexto exige que la base legal sea el consentimiento del usuario, esta mutación gatilla una violación directa por la falta de un control mandatorio.
* `remove_privacy_notice`:
  * **Clase asociada:** `RemoveEventMutation("privacy_notice_disclosed")`
  * **Propósito:** Elimina el evento de divulgación del aviso de privacidad. Provoca un incumplimiento directo del derecho de información transparente estipulado en el Artículo 13 del RGPD.
* `remove_encryption`:
  * **Clase asociada:** `RemoveEventMutation("encryption_applied")`
  * **Propósito:** Suprime el evento que confirma la aplicación de cifrado sobre los datos recolectados, dejando al descubierto una vulnerabilidad en los principios de integridad y confidencialidad (Art. 32).
* `duplicate_confirm_data_erasure`:
  * **Clase asociada:** `DuplicateEventMutation("confirm_data_erasure")`
  * **Propósito:** Duplica el evento de confirmación de borrado de datos. Está diseñado específicamente para forzar y validar alertas de inserción incorrecta o inconsistencias estructurales en las fases de cierre de caso (`CASE_END`).
* `replace_encryption_with_retention`:
  * **Clase asociada:** `ReplaceEventMutation("encryption_applied", "retention_period_verify")`
  * **Propósito:** Sustituye el evento de cifrado técnico por una verificación de periodos de retención. Introduce un "falso positivo" estructural: la traza mantiene la longitud esperada, pero camufla la omisión de una medida de seguridad crítica mediante otra actividad legal no equivalente.

### 4.2. Mutaciones Temporales (`MutationCategory.TEMPORAL`)

Se enfocan en corromper el flujo cronológico y la ordenación secuencial de los eventos de cumplimiento respecto a las actividades operativas del negocio.

* `wrong_position_verify_legal_basis`:
  * **Clase asociada:** `WrongPositionMutation("verify_legal_basis")`
  * **Propósito:** Altera la propiedad de posición o secuencia del evento de verificación base. Provoca que el evento ocurra fuera del marco cronológico permitido por el validador determinista.
* `wrong_position_encryption`:
  * **Clase asociada:** `WrongPositionMutation("encryption_applied")`
  * **Propósito:** Desplaza la marca posicional del evento de cifrado, forzando escenarios donde los datos se procesan o transmiten temporalmente antes de que la medida técnica de protección sea efectivamente registrada.
* `swap_consent_and_collection`:
  * **Clase asociada:** `SwapEventOrderMutation("check_consent", "record_purpose")`
  * **Propósito:** Intercambia los índices de orden entre la verificación de consentimiento (`check_consent`) y el registro de la finalidad (`record_purpose`), rompiendo la coherencia de precondiciones temporales.
* `swap_collection_and_privacy_notice`:
  * **Clase asociada:** `SwapEventOrderMutation("DATA_COLLECTION", "privacy_notice_disclosed")`
  * **Propósito:** Intercambia el orden de la recolección de datos operativos y la notificación de privacidad. Mueve `privacy_notice_disclosed` a una posición previa a la recolección, desafiando las reglas específicas que exigen la traza posicional inversa o posterior según la lógica del flujo de datos implementado.
* `swap_identity_verification_and_response`:
  * **Clase asociada:** `SwapEventOrderMutation("verify_request_identity", "respond_user_right")`
  * **Propósito:** Rompe la cadena temporal de los derechos de los ciudadanos (ARCO+). Fuerza al sistema a simular que se responde o procesa la solicitud de un derecho (`respond_user_right`) *antes* de haber verificado fehacientemente la identidad del reclamante (`verify_request_identity`).

### 4.3. Mutaciones Contextuales (`MutationCategory.CONTEXTUAL`)

Manipulan los atributos del objeto de entorno (`trace.context`), desalineando las condiciones legales declaradas con los eventos reales que se inyectaron en la traza de auditoría.

* `change_legal_basis_to_contract`:
  * **Clase asociada:** `ModifyLegalBasisMutation("contract")`
  * **Propósito:** Modifica dinámicamente la base jurídica global a `"contract"`. Si la traza original contenía eventos dedicados exclusivamente al flujo de consentimiento, provocará advertencias de minimización o inconsistencias contextuales.
* `change_data_category_to_standard`:
  * **Clase asociada:** `ModifyDataCategoryMutation("DataCategory.STANDARD")`
  * **Propósito:** Reduce el nivel de sensibilidad del contexto a datos estándar. Se utiliza para verificar si el validador descarta adecuadamente exigencias severas de seguridad que solo aplican a datos protegidos.
* `change_data_category_to_health`:
  * **Clase asociada:** `ModifyDataCategoryMutation("DataCategory.HEALTH")`
  * **Propósito:** Eleva la categoría de datos a datos sanitarios. Esto fuerza al sistema a exigir salvaguardas avanzadas y bases explícitas de tratamiento conforme al Artículo 9 del RGPD.
* `change_data_category_to_special`:
  * **Clase asociada:** `ModifyDataCategoryMutation("DataCategory.SPECIAL")`
  * **Propósito:** Cambia la categoría a categorías especiales de datos. Su fin es activar y disparar reglas de validación severas, como la obligación mandatoria de realizar un chequeo de control de accesos restringido (`access_control_check`).
* `modify_context_third_party_to_false`:
  * **Clase asociada:** `ModifyContextFieldMutation("has_third_party_recipients", False)`
  * **Propósito:** Establece falsamente que no existen destinatarios externos en el procesamiento. Se usa para verificar si el sistema lanza alertas o advertencias del tipo `DATA_TRANSFER_THIRD_PARTY_FORBIDDEN` en caso de encontrar eventos de envío de datos remotos en la traza real.
* `modify_context_third_party_to_true`:
  * **Clase asociada:** `ModifyContextFieldMutation("has_third_party_recipients", True)`
  * **Propósito:** Fuerza el atributo de destinatarios externos a verdadero. En una traza limpia que carezca de eventos de comunicación, esta mutación genera la obligatoriedad contextual de registrar contratos de encargo de tratamiento o cláusulas de cesión.
* `modify_context_international_to_third_country`:
  * **Clase asociada:** `ModifyContextFieldMutation("international_transfer", "third_country")`
  * **Propósito:** Altera el destino de las transferencias de datos a un tercer país fuera del Espacio Económico Europeo. Esto hace saltar inmediatamente la regla `DATA_TRANSFER_INTERNATIONAL_REQUIRED` para exigir la adición de garantías adecuadas (ej. Cláusulas Contractuales Tipo).
* `clear_context_retention_period`:
  * **Clase asociada:** `ModifyContextFieldMutation("retention_period", None)`
  * **Propósito:** Remueve por completo el periodo de retención configurado en el contexto. Su objetivo es gatillar la violación determinista `CASE_END_MISSING_RETENTION_CONTEXT` al intentar cerrar un caso sin plazos límites definidos de conservación (Principio de limitación del plazo de conservación).

### 4.4. Mutaciones Semánticas / Cadenas de Cumplimiento (`MutationCategory.SEMANTIC`)

Alteran dependencias lógicas complejas y transiciones de estado multi-evento. No manipulan propiedades aisladas, sino la integridad semántica de flujos completos que abarcan múltiples fases del ciclo de vida del dato.

* `break_initial_compliance_chain`:
  * **Clase asociada:** `BreakInitialChainMutation()`
  * **Propósito:** Extrae el evento `verify_legal_basis` de su zona legítima tras el `CASE_START` y lo desplaza de manera posterior a una actividad operativa de captura de datos (`DATA_COLLECTION`). Rompe el principio fundamental de que ninguna recolección puede ejecutarse sin una base legal previamente establecida en la traza.
* `corrupt_user_right_type_to_erasure`:
  * **Clase asociada:** `ModifyUserRightTypeMutation(to_type="UserRightType.ERASURE")`
  * **Propósito:** Cambia el subtipo lógico de una solicitud de derecho de usuario (por ejemplo, mutar un flujo que originalmente correspondía a un derecho de Rectificación hacia uno de Supresión / `ERASURE`). Esto deja los eventos subsiguientes de la traza "huérfanos" de su lógica regulatoria original (por ejemplo, se ejecutarán acciones de modificación sobre registros cuando semánticamente el contexto exige ahora la purga total, corrompiendo la atención al derecho del ciudadano).
* `incomplete_deletion_chain`:
  * **Clase asociada:** `RemoveEventMutation("erase_data")`
  * **Propósito:** Simula un cumplimiento parcial o defectuoso en la cadena de destrucción física de la información. El sistema mantiene intacto el evento formal de verificación de plazos (`record_retention_period`), pero elimina la ejecución del evento técnico de purga real de las bases de datos (`erase_data`). Genera una brecha de cumplimiento crítico donde el proceso aparenta administrativamente haber concluido con éxito pero mantiene los datos almacenados de forma ilícita.
