# tests/test_sticky_policies/test_sp_third_party_after_erasure.py

from datetime import datetime, timedelta

from gdpr.sticky_policies import build_sticky_policy_from_trace
from gdpr.validators.sticky_policy import validate_sticky_policy


class DummyTrace(list):
    """
    Traza mínima para tests de Sticky Policy.
    """
    def __init__(self):
        super().__init__()
        self.attributes = {
            "concept:name": "user_profile"
        }


def test_third_party_active_after_erasure():
    """
    Un tercero no puede seguir activo tras el borrado de los datos.
    (SP-only validation)
    """

    trace = DummyTrace()

    t0 = datetime(2024, 1, 1, 10, 0, 0)

    # 1️⃣ Consentimiento
    trace.append({
        "concept:name": "gdpr:giveConsent",
        "time:timestamp": t0,
        "gdpr:purpose": "service_provision",
        "gdpr:max_time_days": 365
    })

    # 2️⃣ Compartición con tercero
    trace.append({
        "concept:name": "gdpr:shareDataWithThirdParty",
        "time:timestamp": t0 + timedelta(days=1),
        "gdpr:third_party": "AnalyticsProvider",
        "gdpr:purpose": "service_support"
    })

    # 3️⃣ Borrado de datos
    trace.append({
        "concept:name": "gdpr:eraseData",
        "time:timestamp": t0 + timedelta(days=10)
    })

    # 🔧 Reconstruir Sticky Policy
    sp = build_sticky_policy_from_trace(trace)
    trace.attributes["gdpr:sticky_policy"] = sp

    # 🔍 Validar
    violations = validate_sticky_policy(trace)

    # 🧪 Assertions
    types = {v["type"] for v in violations}

    assert "sp_third_party_after_erasure" in types
