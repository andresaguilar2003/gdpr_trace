import json

from app.models.user_right_type import UserRightType
from app.services.ai.roberta_client import RobertaClient
from app.specifications.activity_types import ActivityType


class RobertaActivityClassifier:

    ACTIVITY_LABELS = [
        "data collection",
        "data access",
        "data processing",
        "automated decision",
        "data transfer",
        "storage management",
        "user right request",
        "data deletion",
        "other"
    ]

    ACTIVITY_MAP = {
        "data collection": ActivityType.DATA_COLLECTION,
        "data access": ActivityType.DATA_ACCESS,
        "data processing": ActivityType.DATA_PROCESSING,
        "automated decision": ActivityType.AUTOMATED_DECISION,
        "data transfer": ActivityType.DATA_TRANSFER,
        "storage management": ActivityType.STORAGE_MANAGEMENT,
        "user right request": ActivityType.USER_RIGHT_REQUEST,
        "data deletion": ActivityType.DATA_DELETION,
        "other": ActivityType.OTHER
    }

    USER_RIGHT_LABELS = [
        "access",
        "rectification",
        "erasure",
        "restriction",
        "portability",
        "objection",
        "automated decision review",
        "information",
        "unknown"
    ]

    USER_RIGHT_MAP = {
        "access": UserRightType.ACCESS,
        "rectification": UserRightType.RECTIFICATION,
        "erasure": UserRightType.ERASURE,
        "restriction": UserRightType.RESTRICTION,
        "portability": UserRightType.PORTABILITY,
        "objection": UserRightType.OBJECTION,
        "automated decision review": UserRightType.AUTOMATED_DECISION_REVIEW,
        "information": UserRightType.INFORMATION,
        "unknown": UserRightType.UNKNOWN
    }

    @classmethod
    def classify(cls, activity_profiles, dataset_context=None):
        mapping = {}

        for profile in activity_profiles:
            name = profile.get("name")

            if not name:
                continue

            text = cls._build_activity_text(profile, dataset_context)
            activity_type = cls._classify_activity(name, text)
            user_right_type = None

            if activity_type == ActivityType.USER_RIGHT_REQUEST:
                user_right_type = cls._classify_user_right(name, text)

            mapping[name] = {
                "activity_type": activity_type,
                "user_right_type": user_right_type
            }

        return mapping

    @staticmethod
    def _build_activity_text(profile, dataset_context):
        name = profile.get("name", "")
        attributes = profile.get("example_attributes", {})

        if isinstance(attributes, dict):
            attributes = list(attributes.keys())

        return (
            f"Dataset context: {dataset_context or 'unknown'}. "
            f"Activity name: {name}. "
            f"Observed attributes: {json.dumps(attributes)}."
        )

    @classmethod
    def _classify_activity(cls, name, text):
        heuristic = cls._heuristic_activity_type(name)

        if heuristic is not None:
            return heuristic

        label, _ = RobertaClient.classify(
            text,
            cls.ACTIVITY_LABELS,
            hypothesis_template="This activity is an example of {}."
        )

        return cls.ACTIVITY_MAP.get(label, ActivityType.OTHER)

    @staticmethod
    def _heuristic_activity_type(name):
        lower_name = name.lower()

        if lower_name in {"case_start", "start"}:
            return ActivityType.CASE_START

        if lower_name in {"case_end", "end"}:
            return ActivityType.CASE_END

        # =====================================================
        # DATA_COLLECTION (Ingreso de datos en el sistema)
        # =====================================================
        if any(word in lower_name for word in [
            "register", "registration", "collect", "intake", 
            "enroll", "submit application", "admission",
            "create application", "submitted" # Eventos de préstamos bancarios
        ]):
            return ActivityType.DATA_COLLECTION

        # =====================================================
        # DATA_ACCESS (Consultas directas)
        # =====================================================
        if any(word in lower_name for word in [
            "view", "access", "consult", "read", "retrieve"
        ]):
            return ActivityType.DATA_ACCESS

        # =====================================================
        # DATA_DELETION (Destrucción o purgas)
        # =====================================================
        if any(word in lower_name for word in [
            "delete", "erase", "purge", "destroy", "anonym"
        ]):
            return ActivityType.DATA_DELETION

        # =====================================================
        # DATA_TRANSFER (Comunicaciones e intercambios)
        # =====================================================
        if any(word in lower_name for word in [
            "transfer", "send", "share", "third party", "external",
            "o_sent" # Envío físico/digital de la oferta de préstamos
        ]):
            return ActivityType.DATA_TRANSFER

        # =====================================================
        # AUTOMATED_DECISION (Cálculos de elegibilidad / Scoring)
        # =====================================================
        if any(word in lower_name for word in [
            "score", "decision", "approval", "reject", "classification",
            "a_concept", "a_accepted", "o_create offer", "o_created", "o_accepted" # Evaluación crediticia automática
        ]):
            return ActivityType.AUTOMATED_DECISION

        # =====================================================
        # USER_RIGHT_REQUEST (Ejercicio de derechos ARCO+)
        # =====================================================
        if any(word in lower_name for word in [
            "right", "request access", "rectification", "erasure", 
            "portability", "objection", "restriction"
        ]):
            return ActivityType.USER_RIGHT_REQUEST

        # =====================================================
        # STORAGE_MANAGEMENT (Gestión de ciclo de vida en BD)
        # =====================================================
        if any(word in lower_name for word in [
            "archive", "store", "retention", "close", "release",
            "a_complete", "a_pending" # Estados de persistencia/espera del expediente de préstamo
        ]):
            return ActivityType.STORAGE_MANAGEMENT

        # =====================================================
        # DATA_PROCESSING (Tratamiento, análisis clínicos, validación manual)
        # =====================================================
        if any(word in lower_name for word in [
            "test", "triage", "diagnose", "treat", "process", 
            "calculate", "validate", "check", "assess", "review", "evaluate",
            # --- NUEVOS EVENTOS MÉDICOS ---
            "crp", "leucocytes", "lacticacid", "iv antibiotics", "iv liquid",
            "return er", "er triage", "er sepsis triage", "admission ic", "admission nc",
            # --- NUEVOS EVENTOS DE PRÉSTAMOS (Gestión/Validación manual) ---
            "handle leads", "complete application", "call after offers", 
            "validate application", "a_validating", "o_returned", "call incomplete files", "a_incomplete"
        ]):
            return ActivityType.DATA_PROCESSING

        return None

    @classmethod
    def _classify_user_right(cls, name, text):
        lower_name = name.lower()

        for label, enum_value in cls.USER_RIGHT_MAP.items():
            if label != "unknown" and label in lower_name:
                return enum_value

        label, _ = RobertaClient.classify(
            text,
            cls.USER_RIGHT_LABELS,
            hypothesis_template="This user rights request is about {}."
        )

        return cls.USER_RIGHT_MAP.get(label, UserRightType.UNKNOWN)
