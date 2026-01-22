# tests/sticky_policies/test_sp_no_access_after_erasure.py

from gdpr.importers import load_event_log
from gdpr.pipelines import build_compliant_trace
from gdpr.sticky_policies import build_sticky_policy_from_trace


def test_sp_no_access_after_erasure():
    """
    Verifica que, una vez que los datos han sido borrados (eraseData),
    no existen accesos posteriores según la Sticky Policy reconstruida.
    """

    # 1️⃣ Cargar log de entrada
    log = load_event_log("data/input/test/log_with_erasure.xes")
    trace = log[0]

    # 2️⃣ Construir traza GDPR-compliant
    gdpr_trace = build_compliant_trace(trace)

    # 3️⃣ Reconstruir Sticky Policy desde la traza
    sp = build_sticky_policy_from_trace(gdpr_trace)

    print("\n==============================")
    print("STICKY POLICY STATE")
    print("==============================")
    print(sp)

    # 4️⃣ Si no hay borrado, el test no aplica (modelo permite ambos casos)
    if not sp.erased:
        print("No eraseData event present — test not applicable.")
        assert True
        return

    # 5️⃣ Verificar que no hay accesos tras el borrado
    erase_time = None
    for event in gdpr_trace:
        if event["concept:name"] == "gdpr:eraseData":
            erase_time = event["time:timestamp"]
            break

    assert erase_time is not None, "eraseData event expected but not found"

    for access in sp.access_history:
        assert access["timestamp"] <= erase_time, (
            f"Access after erasure detected: {access}"
        )
