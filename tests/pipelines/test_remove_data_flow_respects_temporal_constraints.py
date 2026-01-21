# tests/pipelines/test_remove_data_flow_respects_temporal_constraints.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.vocabulary import GDPR_EVENTS


def test_remove_data_flow_respects_temporal_constraints():
    """
    Verifica que el flujo de borrado de datos personales (Figura 3):
    - removeData → searchDataLocation → eraseData
    está bien formado y respeta las restricciones temporales legales.
    """

    # 1️⃣ Cargar log real y construir traza GDPR-compliant
    log = load_event_log("data/input/test/log_long_case.xes")
    trace = build_compliant_trace(log[0])

    consent = None
    remove_request = None
    search_location = None
    erase_data = None

    # 2️⃣ Localizar eventos relevantes en la traza
    for e in trace:
        if e["concept:name"] == GDPR_EVENTS["CONSENT"]:
            consent = e
        elif e["concept:name"] == GDPR_EVENTS["REMOVE_REQUEST"]:
            remove_request = e
        elif e["concept:name"] == GDPR_EVENTS["SEARCH_LOCATION"]:
            search_location = e
        elif e["concept:name"] == GDPR_EVENTS["ERASE"]:
            erase_data = e

    print("\n==============================")
    print("REMOVE DATA FLOW INSPECTION")
    print("==============================")

    # 3️⃣ El flujo es opcional → si no existe, el test pasa
    if remove_request is None:
        print("No remove-data flow present in this trace (allowed by the model).")
        return

    # 4️⃣ Comprobaciones estructurales básicas
    assert consent is not None, "Remove request without prior consent"
    assert search_location is not None, "removeData without searchDataLocation"
    assert erase_data is not None, "removeData without eraseData"

    # 5️⃣ Mostrar línea temporal para inspección humana
    print(f"Consent at:             {consent['time:timestamp']}")
    print(f"Remove request at:      {remove_request['time:timestamp']}")
    print(f"Search location at:     {search_location['time:timestamp']}")
    print(f"Erase data at:          {erase_data['time:timestamp']}")
    print(f"Erase deadline (legal): {erase_data.get('gdpr:deadline')}")

    # 6️⃣ Validar orden temporal correcto (Figura 3)
    assert (
        consent["time:timestamp"] < remove_request["time:timestamp"]
    ), "Remove request occurs before consent"

    assert (
        remove_request["time:timestamp"] < search_location["time:timestamp"]
    ), "searchDataLocation occurs before removeData"

    assert (
        search_location["time:timestamp"] < erase_data["time:timestamp"]
    ), "eraseData occurs before searchDataLocation"

    # 7️⃣ Validar restricción temporal legal
    deadline = erase_data.get("gdpr:deadline")
    assert deadline is not None, "eraseData event has no legal deadline"

    assert (
        erase_data["time:timestamp"] <= deadline
    ), "eraseData executed after legal deadline"

    # 8️⃣ Comprobaciones GDPR mínimas
    for ev in (remove_request, search_location, erase_data):
        assert ev.get("gdpr:event") is True, "Event is not marked as GDPR event"
        assert ev.get("gdpr:actor") is not None, "Missing GDPR actor"
        assert ev.get("gdpr:purpose") is not None, "Missing GDPR purpose"
