# Experimento de Evaluacion: Phi-3 vs RoBERTa

## Objetivo

Este experimento compara el comportamiento del modelo anterior, Phi-3, frente al modelo actual, RoBERTa, en dos tareas usadas por el sistema de enriquecimiento GDPR:

1. Inferencia del contexto global del dataset, rellenando los atributos de `Context`.
2. Tipado de actividades individuales, asignando cada evento a un valor de `ActivityType`.

La hipotesis de trabajo es que RoBERTa, al funcionar como clasificador semantico de tipo zero-shot apoyado por reglas de dominio, ofrece resultados mas estables para vocabularios de negocio y RGPD que Phi-3, que dependia de generacion libre via prompt y podia devolver JSON incompleto, etiquetas inventadas o tipados inconsistentes.

## Codigo Analizado

La ruta activa de RoBERTa esta en:

- `app/services/ai/roberta_client.py`: encapsula el pipeline de Hugging Face `zero-shot-classification` usando `FacebookAI/roberta-large-mnli`.
- `app/services/ai/roberta_trace_context_inferer.py`: infiere el contexto global del log.
- `app/services/ai/roberta_activity_classifier.py`: clasifica actividades hacia `ActivityType`.

La ruta preservada de Phi-3 esta en:

- `app/services/llm_client.py`: cliente Ollama con `phi3:latest`.
- `app/services/trace_context_inferer.py`: metodo `infer_dataset_context_with_phi3`.
- `app/services/activity_classifier.py`: metodo `classify_with_phi3`.

El script de evaluacion no usa la ruta normal de produccion, porque esa ruta ya delega en RoBERTa. Para comparar ambos modelos de forma justa, llama explicitamente a los metodos RoBERTa y Phi-3.

## Datos Utilizados

El script esta preparado para buscar datasets reales en:

1. `data/input`

En este workspace concreto, la carpeta existente con los `.xes` reales es `data/input`:

- `data/input/Sepsis Cases - Event Log.xes.gz`
- `data/input/BPI Challenge 2017.xes.gz`

Para evitar usar datos ficticios, el script carga los `.xes` reales con `pm4py`, los convierte a trazas internas mediante `build_traces_from_pm4py_log` y extrae las actividades reales presentes en cada log.

## Ground Truth

Los datasets reales no incluyen una etiqueta GDPR canonica para `Context` ni para `ActivityType`. Por tanto, el experimento define un ground truth experto basado en el vocabulario real de los dos logs.

Para Sepsis:

- Dominio esperado: `healthcare`.
- Proposito esperado: `medical_treatment`.
- Base legal esperada: `legal_obligation`.
- Categoria de datos esperada: `health`.
- Sujeto esperado: `patient`.
- Actividades como `CRP`, `Leucocytes`, `LacticAcid`, `ER Triage` e `IV Antibiotics` se etiquetan como `DATA_PROCESSING`.
- `ER Registration` se etiqueta como `DATA_COLLECTION`.
- Eventos `Release A`, `Release B`, etc. se etiquetan como `STORAGE_MANAGEMENT`, ya que representan cierre/salida o gestion del ciclo de vida del caso, no borrado de datos.

Para BPI Challenge 2017:

- Dominio esperado: `banking`.
- Proposito esperado: `contract_execution`.
- Base legal esperada: `contract`.
- Categoria de datos esperada: `standard`.
- Sujeto esperado: `customer`.
- Eventos como `A_Create Application` y `A_Submitted` se etiquetan como `DATA_COLLECTION`.
- Tareas manuales `W_*`, validaciones y llamadas se etiquetan como `DATA_PROCESSING`.
- Eventos de oferta o decision como `A_Accepted`, `O_Create Offer`, `O_Accepted` se etiquetan como `AUTOMATED_DECISION`.
- Eventos `O_Sent (...)` se etiquetan como `DATA_TRANSFER`.
- Estados terminales o persistentes como `A_Complete`, `A_Pending` y `A_Cancelled` se etiquetan como `STORAGE_MANAGEMENT`.

El ground truth esta dentro de `experiments/evaluate_models.py` para que el experimento sea autocontenido y reproducible.

## Metodologia

1. Se cargan los logs reales desde `data/input`.
2. Cada log se convierte a trazas internas del repositorio.
3. Se construyen perfiles de actividad, agrupando nombres de actividad y atributos observados.
4. Para cada dataset se ejecutan dos tareas:
   - Inferencia de contexto global.
   - Clasificacion de actividades etiquetadas.
5. Para Phi-3:
   - Contexto: `TraceContextInferer.infer_dataset_context_with_phi3`.
   - Actividades: `ActivityClassifier.classify_with_phi3`.
6. Para RoBERTa:
   - Contexto: `RobertaTraceContextInferer.infer_dataset_context`.
   - Actividades: `RobertaActivityClassifier.classify`.
7. Las predicciones se normalizan para poder comparar enums, strings y valores booleanos.
8. Se calculan metricas con scikit-learn:
   - Accuracy.
   - Precision macro, micro y weighted.
   - Recall macro, micro y weighted.
   - F1 macro, micro y weighted.
   - Classification report completo.
   - Matriz de confusion para contexto y para `ActivityType`.

## Ejecucion

Instalar dependencias necesarias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```

Ejecutar el experimento completo en modo rapido:

```powershell
.\.venv\Scripts\python.exe experiments\evaluate_models.py
```

## Interpretacion Esperada

RoBERTa deberia ser mas estable en:

- Tipado de eventos clinicos como `CRP`, `Leucocytes`, `LacticAcid` o `ER Triage`.
- Identificacion del dominio sanitario y categoria `health` en Sepsis.
- Reconocimiento de flujo financiero/contractual en BPI.
- Reduccion de errores de formato, porque no genera JSON libre para el tipado.

Phi-3 puede funcionar bien cuando el prompt se responde de forma limpia, pero su evaluacion queda mas expuesta a:

- JSON mal formado.
- Etiquetas no existentes en `ActivityType`.
- Omisiones de actividades.
- Respuestas generativas con explicaciones adicionales.
- Dependencia de que Ollama este instalado y el modelo `phi3:latest` disponible.

Si Phi-3 falla durante la ejecucion, el script no se detiene. Registra la excepcion en `evaluation_results.json` y marca las predicciones afectadas como `__ERROR__`, lo cual permite que la comparacion siga siendo auditable.

## Limitaciones

El ground truth es experto y esta basado en el vocabulario de los logs reales, pero no procede de una anotacion oficial incluida en los `.xes`. Por tanto, las metricas deben interpretarse como una evaluacion controlada de adecuacion semantica al marco GDPR del proyecto, no como benchmark publico externo.

La evaluacion por defecto usa un limite de trazas para hacer viable la ejecucion en local. Como las etiquetas se evaluan sobre nombres de actividad unicos, este limite suele ser suficiente para capturar el vocabulario principal. Para un informe final, conviene ejecutar con `--max-traces 0`.
