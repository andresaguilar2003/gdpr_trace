# gdpr/pipelines.py

from gdpr.generators import (
    insert_initial_consent_flow,
    insert_consent_expiration,
    insert_remove_data_flow,
    insert_rectification,
    insert_processing_restriction,
    enrich_real_events_with_gdpr,
    insert_access_logs_and_history,
    insert_breach_events,
    insert_data_subject_rights
)
from gdpr.utils import sort_trace_by_time


def build_compliant_trace(trace):
    """
    Construye una traza GDPR-compliant a partir de una traza real.
    Implementa las Figuras 3–6 del modelo GDPR.
    """

    # =====================================================
    # 1) CONTEXTO GDPR A NIVEL DE TRAZA (CLAVE)
    # =====================================================
    trace.attributes.setdefault("gdpr:personal_data", True)
    trace.attributes.setdefault("gdpr:data_subject", "data_subject")
    trace.attributes.setdefault("gdpr:data_controller", "Controller")
    trace.attributes.setdefault("gdpr:legal_basis", "consent")
    trace.attributes.setdefault("gdpr:default_purpose", "service_provision")
    trace.attributes.setdefault("gdpr:processing_scope", "full")


    # =====================================================
    # 2) FLUJOS GDPR (eventos)
    # =====================================================
    insert_initial_consent_flow(
        trace,
        default_purpose=trace.attributes["gdpr:default_purpose"]
    )

    insert_consent_expiration(trace)
    insert_remove_data_flow(trace)
    insert_rectification(trace)
    insert_processing_restriction(trace)

    enrich_real_events_with_gdpr(trace)
    insert_access_logs_and_history(trace)

    insert_breach_events(trace)
    insert_data_subject_rights(trace)

    sort_trace_by_time(trace)

    # =====================================================
    # 3) MARCADO FINAL
    # =====================================================
    trace.attributes["gdpr:compliance"] = "compliant"

    return trace




from gdpr.generators import generate_non_compliant_trace

def build_non_compliant_trace(trace):
    """
    Genera una versión NO conforme de una traza GDPR-compliant.
    Introduce una violación aleatoria del modelo.
    """
    return generate_non_compliant_trace(trace)
