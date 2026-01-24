# gdpr/generators.py
import copy
from random import choice, sample
from gdpr.vocabulary import GDPR_EVENTS
from gdpr.utils import sort_trace_by_time, get_first_event_timestamp
from datetime import timedelta
from random import random, randint
from pm4py.objects.log.obj import Event

# ============================================================
# FUNCIONES BASE
# ============================================================
# Funciones genéricas reutilizadas en todo el fichero

from datetime import timedelta
from pm4py.objects.log.obj import Event

def create_gdpr_event(name, timestamp, actor="Controller", purpose=None):
    """
    Crea un evento GDPR.
    Este patrón se corresponde con los mensajes UML
    de los diagramas de secuencia del artículo.
    """
    event = Event()
    event["concept:name"] = name
    event["time:timestamp"] = timestamp
    event["gdpr:event"] = True
    event["gdpr:actor"] = actor
    
    if purpose:
        event["gdpr:purpose"] = purpose
    
    return event

def create_send_data_event(timestamp, max_time_days):
    event = create_gdpr_event(
        name=GDPR_EVENTS["SEND_DATA"],
        timestamp=timestamp,
        actor="User",
        purpose="data_provision"
    )
    event["gdpr:maxTime"] = max_time_days
    event["gdpr:is_processing"] = False  # CLAVE
    return event


def create_consent_expired_event(timestamp):
    """
    Evento que representa la expiración del consentimiento
    cuando se supera maxTime (Figura 3: loop [time <= maxTime]).
    """
    return create_gdpr_event(
        name=GDPR_EVENTS["CONSENT_EXPIRED"],
        timestamp=timestamp,
        actor="Controller",
        purpose="consent_expiration"
    )



# ============================================================
# FIGURA 3 – INICIO DEL TRATAMIENTO
# (informUser -> giveConsent)
# ============================================================
# Según la Figura 3, el usuario debe:
# 1) Ser informado
# 2) Dar consentimiento
# antes de cualquier acceso a datos personales. (Todo esto es ANTES del SD MAIN)
def insert_initial_consent_flow(trace, default_purpose="service_provision"):
    """
    Figura 3 – Inicio del tratamiento:
    sendData → inform → consent
    """
    first_ts = get_first_event_timestamp(trace)

    send_data_event = create_send_data_event(
        timestamp=first_ts - timedelta(minutes=15),
        max_time_days=365
    )

    inform_event = create_gdpr_event(
        GDPR_EVENTS["INFORM"],
        first_ts - timedelta(minutes=10),
        actor="Controller",
        purpose="service_t"
    )

    consent_event = create_gdpr_event(
        GDPR_EVENTS["CONSENT"],
        first_ts - timedelta(minutes=5),
        actor="User",
        purpose=default_purpose
    )
    consent_event["gdpr:consent_type"] = "explicit"
    consent_event["gdpr:scope"] = "full"

    trace.insert(0, send_data_event)
    trace.insert(1, inform_event)
    trace.insert(2, consent_event)



# ============================================================
# FIGURA 3 – EXPIRACIÓN DEL CONSENTIMIENTO (loop maxTime)
# ============================================================

def insert_consent_expiration(trace):
    """
    Inserta un evento consentExpired cuando se supera maxTime,
    según la Figura 3 (Salir del loop).
    """
    send_event = None
    consent_event = None

    # Localizar sendData y giveConsent
    for event in trace:
        if event["concept:name"] == GDPR_EVENTS["SEND_DATA"]:
            send_event = event
        elif event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = event

    if not send_event or not consent_event:
        return  # seguridad

    max_time_days = send_event.get("gdpr:maxTime")
    if not max_time_days:
        return

    # Momento de expiración
    expiration_ts = consent_event["time:timestamp"] + timedelta(days=max_time_days)

    # Evitar duplicados
    for event in trace:
        if event["concept:name"] == GDPR_EVENTS["CONSENT_EXPIRED"]:
            return

    # Insertar evento de expiración
    trace.append(create_consent_expired_event(expiration_ts))



# ============================================================
# FIGURA 3 – REMOVE DATA (removeData → searchDataLocation → eraseData)
# con restricción temporal
# ============================================================

REMOVE_PROBABILITY = 0.1
MAX_ERASE_DAYS = 7
from random import random, randint
from datetime import timedelta


# ------------------------------------------------------------
# Eventos GDPR adicionales (Figura 3)
# ------------------------------------------------------------

def create_remove_request_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["REMOVE_REQUEST"],
        timestamp=timestamp,
        actor="User",
        purpose="right_to_erasure"
    )


def create_search_location_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["SEARCH_LOCATION"],
        timestamp=timestamp,
        actor="Controller",
        purpose="locate_personal_data"
    )


def create_erase_data_event(timestamp, deadline_ts):
    event = create_gdpr_event(
        name=GDPR_EVENTS["ERASE"],
        timestamp=timestamp,
        actor="Processor",
        purpose="data_erasure"
    )
    event["gdpr:deadline"] = deadline_ts
    event["gdpr:temporal_constraint"] = "within_legal_time"
    return event


# ------------------------------------------------------------
# Inserción correcta según el diagrama UML
# ------------------------------------------------------------
def insert_remove_data_flow(trace):
    if random() > REMOVE_PROBABILITY:
        return

    # El usuario solo puede pedir borrado tras haber dado consentimiento
    consent_event = None
    for event in trace:
        if event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = event

    if consent_event is None:
        return

    # removeData(Data)
    remove_ts = consent_event["time:timestamp"] + timedelta(days=1)
    remove_event = create_remove_request_event(remove_ts)
    trace.append(remove_event)

    # searchDataLocation
    search_ts = remove_ts + timedelta(hours=1)
    search_event = create_search_location_event(search_ts)
    trace.append(search_event)

    # eraseData(Data, machines) con restricción temporal
    erase_delay = randint(1, MAX_ERASE_DAYS)
    deadline_ts = remove_ts + timedelta(days=MAX_ERASE_DAYS)
    erase_ts = remove_ts + timedelta(days=erase_delay)

    erase_event = create_erase_data_event(erase_ts, deadline_ts)
    trace.append(erase_event)

    # Marcar accesos posteriores como violación
    for event in trace:
        if event.get("gdpr:access") and event["time:timestamp"] > erase_ts:
            event["gdpr:violation"] = "access_after_erasure"



# ============================================================
# FIGURA 3 – DERECHO DE RECTIFICACIÓN
# ============================================================

RECTIFY_PROBABILITY = 0.15   # 15% de las trazas

def create_rectify_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["RECTIFY"],
        timestamp=timestamp,
        actor="Controller",
        purpose="data_rectification"
    )

def insert_rectification(trace):
    if random() > RECTIFY_PROBABILITY:
        return

    # Buscar consentimiento
    for i, event in enumerate(trace):
        if event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            base_ts = trace[i + 1]["time:timestamp"]
            rectify_ts = base_ts + timedelta(days=2)

            trace.insert(i + 2, create_rectify_event(rectify_ts))
            break


# ============================================================
# FIGURA 3 – RESTRICCIÓN DEL TRATAMIENTO
# ============================================================

RESTRICT_PROBABILITY = 0.1
RESTRICTION_DAYS = 30

def create_restrict_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["RESTRICT"],
        timestamp=timestamp,
        actor="User",
        purpose="restrict_processing"
    )

def create_lift_restriction_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["LIFT_RESTRICTION"],
        timestamp=timestamp,
        actor="Controller",
        purpose="lift_processing_restriction"
    )

def insert_processing_restriction(trace):
    if random() > RESTRICT_PROBABILITY:
        return

    for i, event in enumerate(trace):
        if event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            restrict_ts = trace[i + 1]["time:timestamp"] + timedelta(days=3)
            lift_ts = restrict_ts + timedelta(days=RESTRICTION_DAYS)

            trace.insert(i + 2, create_restrict_event(restrict_ts))
            trace.insert(i + 3, create_lift_restriction_event(lift_ts))
            break


# ============================================================
# FIGURA 4 – ACCESO A DATOS Y TRAZABILIDAD
# ============================================================

from pm4py.objects.log.obj import Event
from datetime import timedelta

# ------------------------------------------------------------
# Clasificación del tipo de acceso
# ------------------------------------------------------------
def classify_data_access(event_name):
    write_verbs = ["create", "update", "modify", "delete", "write", "set", "register"]
    return GDPR_EVENTS["WRITE"] if any(v in event_name.lower() for v in write_verbs) else GDPR_EVENTS["READ"]


# ------------------------------------------------------------
# Evento de autorización explícita (permissionGranted)
# ------------------------------------------------------------
def create_permission_event(timestamp, access_type, purpose, legal_basis):
    event = Event()
    event["concept:name"] = "gdpr:permissionGranted"
    event["time:timestamp"] = timestamp
    event["gdpr:event"] = True
    event["gdpr:actor"] = "Controller"
    event["gdpr:purpose"] = purpose
    event["gdpr:action_type"] = access_type
    event["gdpr:legal_basis"] = legal_basis  # consent / prior_permission
    return event


# ------------------------------------------------------------
# Enriquecer eventos reales con control de acceso GDPR
# ------------------------------------------------------------
def enrich_real_events_with_gdpr(trace):
    consent_valid = True
    restriction_active = False

    i = 0
    while i < len(trace):
        event = trace[i]
        name = event["concept:name"]

        # sendData no es acceso ni tratamiento
        if name == GDPR_EVENTS["SEND_DATA"]:
            i += 1
            continue

        if name in [GDPR_EVENTS["WITHDRAW"], GDPR_EVENTS["CONSENT_EXPIRED"]]:
            consent_valid = False

        if name == GDPR_EVENTS["RESTRICT"]:
            restriction_active = True

        if name == GDPR_EVENTS["LIFT_RESTRICTION"]:
            restriction_active = False

        if event.get("gdpr:event"):
            i += 1
            continue

        if not consent_valid:
            event["gdpr:blocked_reason"] = "missing_or_expired_consent"
            i += 1
            continue

        if restriction_active:
            event["gdpr:blocked_reason"] = "processing_restricted"
            i += 1
            continue


        access_type = classify_data_access(event["concept:name"])

        # Insertar evento de autorización antes del acceso
        permission_event = create_permission_event(
            timestamp=event["time:timestamp"] - timedelta(seconds=1),
            access_type=access_type,
            purpose="service_provision",
            legal_basis="consent"
        )

        trace.insert(i, permission_event)
        i += 1

        event["gdpr:access"] = access_type
        event["gdpr:access_mode"] = "single"  # preparado para combine
        event["gdpr:actor"] = "Controller"
        event["gdpr:purpose"] = "service_provision"

        i += 1


# ------------------------------------------------------------
# Evento AccessLog enriquecido
# ------------------------------------------------------------
def create_access_log_event(access_event):
    log_event = Event()
    log_event["concept:name"] = GDPR_EVENTS["ACCESS_LOG"]
    log_event["time:timestamp"] = access_event["time:timestamp"]
    log_event["gdpr:event"] = True
    log_event["gdpr:actor"] = access_event["gdpr:actor"]
    log_event["gdpr:purpose"] = access_event["gdpr:purpose"]
    log_event["gdpr:related_activity"] = access_event["concept:name"]
    log_event["gdpr:access_type"] = access_event["gdpr:access"]
    log_event["gdpr:authorized"] = True
    log_event["gdpr:authorization_basis"] = "consent"
    return log_event


# ------------------------------------------------------------
# Evento de actualización del historial del SP
# ------------------------------------------------------------
def create_access_history_update_event(timestamp):
    event = Event()
    event["concept:name"] = "gdpr:updateAccessHistory"
    event["time:timestamp"] = timestamp
    event["gdpr:event"] = True
    event["gdpr:actor"] = "Controller"
    event["gdpr:purpose"] = "accountability"
    return event


# ------------------------------------------------------------
# Inserción de accessLog y cierre del ciclo
# ------------------------------------------------------------
def insert_access_logs_and_history(trace):
    i = 0
    last_log_ts = None

    while i < len(trace):
        if trace[i].get("gdpr:access"):
            access_log = create_access_log_event(trace[i])
            trace.insert(i + 1, access_log)
            last_log_ts = access_log["time:timestamp"]
            i += 1
        i += 1

    if last_log_ts:
        trace.append(create_access_history_update_event(last_log_ts + timedelta(seconds=1)))



# ============================================================
# FIGURA 5 – BRECHAS DE SEGURIDAD ("subscription" METODO DEL LOOP DE LA FIGURA 3)
# ============================================================
# detectBreach → notifyBreach (≤ 72h)

# Simular violaciones de datos
BREACH_PROBABILITY = 0.05     # 5% de las trazas
MAX_NOTIFY_HOURS = 72

# Crear eventos de violación de datos
def create_detect_breach_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["BREACH"],
        timestamp=timestamp,
        actor="Processor",
        purpose="security_incident"
    )

def create_notify_breach_event(timestamp):
    event = create_gdpr_event(
        name=GDPR_EVENTS["NOTIFY_BREACH"],
        timestamp=timestamp,
        actor="Controller",
        purpose="breach_notification"
    )
    event["gdpr:temporal_constraint"] = "within_72_hours"
    return event



# Insertar eventos de violación de datos
def insert_breach_events(trace):
    if random() > BREACH_PROBABILITY:
        return
    
    # Elegir un evento base (último evento con timestamp)
    base_event = max(trace, key=lambda e: e["time:timestamp"])
    
    # Detect breach
    detect_ts = base_event["time:timestamp"] + timedelta(hours=1)
    detect_event = create_detect_breach_event(detect_ts)
    
    trace.append(detect_event)
    
    # Notify breach (≤ 72h)
    notify_delay = randint(1, MAX_NOTIFY_HOURS)
    notify_ts = detect_ts + timedelta(hours=notify_delay)
    notify_event = create_notify_breach_event(notify_ts)
    
    trace.append(notify_event)


# ============================================================
# FIGURA 6 – DERECHOS DEL INTERESADO ("infoDataUser" METODO DEL LOOP DE LA FIGURA 3)
# ============================================================
# requestInfo → provideInfo (≤ 30 días)

# Simular ejercicio de derechos ARCO
RIGHTS_PROBABILITY = 0.2     # 20% de los casos ejercen derechos
MAX_RESPONSE_DAYS = 30
from random import random, randint

# Crear evento de requestInfo
def create_request_info_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["REQUEST_INFO"],
        timestamp=timestamp,
        actor="User",
        purpose="data_management_information"
    )

# Crear evento de provideInfo
def create_provide_info_event(timestamp):
    event = create_gdpr_event(
        name=GDPR_EVENTS["PROVIDE_INFO"],
        timestamp=timestamp,
        actor="Controller",
        purpose="data_management_information"
    )
    event["gdpr:temporal_constraint"] = "within_30_days"
    return event


# Insertar eventos de ejercicio de derechos
def insert_data_subject_rights(trace):
    # Decidir si esta traza ejerce derechos
    if random() > RIGHTS_PROBABILITY:
        return
    
    # Elegimos un punto válido de la traza (después del consentimiento)
    consent_index = None
    for i, event in enumerate(trace):
        if event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_index = i
            break
    
    if consent_index is None:
        return  # No debería pasar, pero seguridad
    
    # Tomamos un evento posterior para colocar la solicitud
    base_event = trace[consent_index + 1]
    request_ts = base_event["time:timestamp"] + timedelta(days=1)
    
    request_event = create_request_info_event(request_ts)
    
    # Insertamos requestInfo
    insert_pos = consent_index + 2
    trace.insert(insert_pos, request_event)
    
    # Generar provideInfo dentro de 30 días
    response_delay = randint(1, MAX_RESPONSE_DAYS)
    provide_ts = request_ts + timedelta(days=response_delay)
    
    provide_event = create_provide_info_event(provide_ts)
    
    trace.insert(insert_pos + 1, provide_event)




# ============================================================
# EXTENSIÓN FIGURA 3 – BORRADO FINAL FUERA DEL LOOP
# (removing SP in log / removing Data & Copies)
# ============================================================

def create_remove_sp_log_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["REMOVE_SP_LOG"],
        timestamp=timestamp,
        actor="Controller",
        purpose="cleanup_processing_state"
    )

def create_erase_all_copies_event(timestamp):
    return create_gdpr_event(
        name=GDPR_EVENTS["ERASE_ALL_COPIES"],
        timestamp=timestamp,
        actor="Controller",
        purpose="final_data_erasure"
    )

def finalize_erasure_after_loop(trace):
    """
    Implementa la parte final de la Figura 3:
    - removing SP in log
    - removing Data & Copies
    """

    last_erase_index = None
    for i, event in enumerate(trace):
        if event["concept:name"] == GDPR_EVENTS["ERASE"]:
            last_erase_index = i

    if last_erase_index is None:
        return  # No hubo derecho de supresión

    base_ts = trace[last_erase_index]["time:timestamp"]

    trace.insert(
        last_erase_index + 1,
        create_remove_sp_log_event(base_ts + timedelta(minutes=5))
    )

    trace.insert(
        last_erase_index + 2,
        create_erase_all_copies_event(base_ts + timedelta(minutes=10))
    )


# ============================================================
# EXTENSIÓN – TERCEROS (Third Parties)
# ============================================================

THIRD_PARTY_PROBABILITY = 0.3
REVOKE_THIRD_PARTY_PROBABILITY = 0.3

THIRD_PARTIES = [
    "AnalyticsProvider",
    "PaymentGateway",
    "CloudStorageProvider"
]


def create_share_data_event(
    timestamp,
    third_party,
    purpose,
    role="processor",
    retention_days=None
):
    """
    Evento GDPR que representa la compartición de datos
    con un tercero (Figura conceptual de terceros).
    """
    event = create_gdpr_event(
        name=GDPR_EVENTS["SHARE_DATA"],
        timestamp=timestamp,
        actor="Controller",
        purpose=purpose
    )

    event["gdpr:third_party"] = third_party
    event["gdpr:role"] = role
    event["gdpr:retention_days"] = retention_days

    # IMPORTANTE:
    # Esto NO es un acceso directo a datos en la traza real
    event["gdpr:is_processing"] = False

    return event


def create_revoke_third_party_event(timestamp, third_party):
    """
    Evento que revoca el acceso de un tercero previamente autorizado.
    """
    event = create_gdpr_event(
        name=GDPR_EVENTS["REVOKE_THIRD_PARTY"],
        timestamp=timestamp,
        actor="Controller",
        purpose="revoke_third_party_access"
    )

    event["gdpr:third_party"] = third_party
    return event


def insert_third_party_flow(trace):
    """
    Inserta un flujo de compartición con terceros:
    consent → share → (optional) revoke
    """
    if random() > THIRD_PARTY_PROBABILITY:
        return

    # 1️⃣ Buscar consentimiento
    consent_event = None
    for event in trace:
        if event["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent_event = event
            break

    if consent_event is None:
        return

    # 2️⃣ Momento base (siempre después del consentimiento)
    base_ts = consent_event["time:timestamp"] + timedelta(days=1)

    third_party = choice(THIRD_PARTIES)

    share_event = create_share_data_event(
        timestamp=base_ts,
        third_party=third_party,
        purpose="service_support",
        role="processor",
        retention_days=90
    )

    trace.append(share_event)

    # 3️⃣ Posible revocación posterior
    if random() < REVOKE_THIRD_PARTY_PROBABILITY:
        revoke_ts = base_ts + timedelta(days=30)

        revoke_event = create_revoke_third_party_event(
            revoke_ts,
            third_party
        )

        trace.append(revoke_event)



###################################################
#######    NON_COMPLIANT   ##########
###################################################


def generate_non_compliant_trace(trace, max_violations=3):
    """
    Genera una versión NO conforme con GDPR a partir de una traza compliant.
    Introduce múltiples violaciones aleatorias.
    """
    new_trace = copy.deepcopy(trace)

    possible_violations = [
        "consent_after_access",
        "missing_consent",
        "late_breach_notification",
        "missing_breach_notification",
        "missing_right_response",
        "late_right_response",
        "access_after_withdrawal",
        "access_during_restriction",
        "erase_without_processing",
        "implicit_consent",
        "purpose_violation",
        "data_minimization_violation",
        "access_after_erasure"
    ]

    n = randint(1, max_violations)
    selected = sample(possible_violations, n)

    new_trace.attributes["gdpr:violation_types"] = selected

    for violation in selected:
        if violation == "consent_after_access":
            _violate_consent_order(new_trace)

        elif violation == "missing_consent":
            _remove_event(new_trace, GDPR_EVENTS["CONSENT"])

        elif violation == "missing_right_response":
            _remove_event(new_trace, GDPR_EVENTS["PROVIDE_INFO"])

        elif violation == "late_right_response":
            _delay_right_response(new_trace)

        elif violation == "late_breach_notification":
            _delay_breach_notification(new_trace)

        elif violation == "missing_breach_notification":
            _remove_event(new_trace, GDPR_EVENTS["NOTIFY_BREACH"])

        elif violation == "access_after_withdrawal":
            _insert_access_after_withdrawal(new_trace)

        elif violation == "access_during_restriction":
            _insert_access_during_restriction(new_trace)

        elif violation == "erase_without_processing":
            _insert_erase_without_processing(new_trace)

        elif violation == "implicit_consent":
            _make_consent_implicit(new_trace)

        elif violation == "purpose_violation":
            _violate_purpose(new_trace)

        elif violation == "data_minimization_violation":
            _excessive_data_access(new_trace)

        elif violation == "access_after_erasure":
            _insert_access_after_erasure(new_trace)


    sort_trace_by_time(new_trace)
    new_trace.attributes["gdpr:compliance"] = "non_compliant"

    return new_trace

def _remove_event(trace, event_name):
    trace._list = [
        e for e in trace if e["concept:name"] != event_name
    ]


def _violate_consent_order(trace):
    """
    Mueve el consentimiento al final de la traza
    para simular consentimiento posterior al acceso.
    """
    consent_events = [
        e for e in trace if e["concept:name"] == GDPR_EVENTS["CONSENT"]
    ]

    if not consent_events:
        return

    consent = consent_events[0]

    # Reconstruir la lista SIN el consentimiento
    new_events = [e for e in trace if e is not consent]

    # Añadir consentimiento al final
    new_events.append(consent)

    trace._list = new_events



def _delay_breach_notification(trace):
    detect = None
    notify = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["BREACH"]:
            detect = e
        elif e["concept:name"] == GDPR_EVENTS["NOTIFY_BREACH"]:
            notify = e

    if detect and notify:
        notify["time:timestamp"] = detect["time:timestamp"] + timedelta(hours=100)

def _insert_access_after_withdrawal(trace):
    withdraw = next(
        (e for e in trace if e["concept:name"] == GDPR_EVENTS["WITHDRAW"]),
        None
    )

    if withdraw:
        access = copy.deepcopy(withdraw)
        access["concept:name"] = "DATA_ACCESS"
        access["gdpr:access"] = True
        access["time:timestamp"] += timedelta(minutes=10)
        trace._list.append(access)


def _insert_access_during_restriction(trace):
    restrict = next(
        (e for e in trace if e["concept:name"] == GDPR_EVENTS["RESTRICT"]),
        None
    )

    if restrict:
        access = copy.deepcopy(restrict)
        access["concept:name"] = "DATA_ACCESS"
        access["gdpr:access"] = True
        access["time:timestamp"] += timedelta(minutes=5)
        trace._list.append(access)

def _insert_erase_without_processing(trace):
    erase = next(
        (e for e in trace if e["concept:name"] == GDPR_EVENTS["ERASE"]),
        None
    )

    if not erase:
        erase_event = copy.deepcopy(trace[0])
        erase_event["concept:name"] = GDPR_EVENTS["ERASE"]
        erase_event["time:timestamp"] += timedelta(minutes=1)
        trace._list.append(erase_event)

def _delay_right_response(trace):
    request = None
    response = None

    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["REQUEST_INFO"]:
            request = e
        elif e["concept:name"] == GDPR_EVENTS["PROVIDE_INFO"]:
            response = e

    if request and response:
        response["time:timestamp"] = request["time:timestamp"] + timedelta(days=45)


def _make_consent_implicit(trace):
    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            e["gdpr:explicit"] = False
            return


def _violate_purpose(trace):
    for e in trace:
        if e.get("gdpr:access"):
            e["gdpr:purpose"] = "unauthorized_purpose"
            return


def _excessive_data_access(trace):
    for e in trace:
        if e.get("gdpr:access"):
            e["gdpr:data_scope"] = "excessive"
            return


def _insert_access_after_erasure(trace):
    erase = next(
        (e for e in trace if e["concept:name"] == GDPR_EVENTS["ERASE"]),
        None
    )

    if erase:
        access = copy.deepcopy(erase)
        access["concept:name"] = "DATA_ACCESS"
        access["gdpr:access"] = True
        access["time:timestamp"] += timedelta(minutes=5)
        trace._list.append(access)



#####################################
#VISTA DE VIOLACIONES
#####################################
from collections import defaultdict

def print_violations_summary(violations):
    grouped = defaultdict(list)

    for v in violations:
        grouped[v["type"]].extend(v.get("events", []))

    print("\nVIOLATIONS SUMMARY")
    print("-" * 40)

    for vtype, events in grouped.items():
        print(f"{vtype}: {len(events)} event(s)")
        for e in events:
            print(
                f"  - {e['time:timestamp']} | {e['concept:name']}"
            )
