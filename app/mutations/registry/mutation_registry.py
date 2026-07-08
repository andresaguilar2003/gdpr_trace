from app.mutations.base.mutation_category import (
    MutationCategory
)

from app.mutations.operators.contextual.modify_context_field_mutation import ModifyContextFieldMutation
from app.mutations.operators.structural.remove_event_mutation import (
    RemoveEventMutation
)
from app.mutations.operators.structural.duplicate_event_mutation import (
    DuplicateEventMutation
)

from app.mutations.operators.structural.replace_event_mutation import ReplaceEventMutation
from app.mutations.operators.temporal.swap_event_order_mutation import (
    SwapEventOrderMutation
)
from app.mutations.operators.temporal.wrong_position_mutation import (
    WrongPositionMutation
)

from app.mutations.operators.contextual.modify_legal_basis_mutation import (
    ModifyLegalBasisMutation
)
from app.mutations.operators.contextual.modify_data_category_mutation import (
    ModifyDataCategoryMutation
)

from app.mutations.operators.semantic.break_initial_compliance_chain_mutation import (
    BreakInitialChainMutation
)
from app.mutations.operators.semantic.modify_user_right_type_mutation import (
    ModifyUserRightTypeMutation
)


# ==========================================================
# REGISTRY EXTENDED
# ==========================================================

MUTATION_REGISTRY = {

    # ======================================================
    # STRUCTURAL (Nivel 1)
    # ======================================================
    # (Tus mutaciones existentes se mantienen...)
    "remove_verify_legal_basis": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: RemoveEventMutation("verify_legal_basis")
    },
    "duplicate_verify_legal_basis": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: DuplicateEventMutation("verify_legal_basis")
    },
    "remove_check_consent": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: RemoveEventMutation("check_consent")
    },
    "remove_privacy_notice": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: RemoveEventMutation("privacy_notice_disclosed")
    },
    "remove_encryption": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: RemoveEventMutation("encryption_applied")
    },

    # Para forzar la alerta de inserción incorrecta (Duplication) en CASE_END
    "duplicate_confirm_data_erasure": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: DuplicateEventMutation("confirm_data_erasure")
    },
    # Mutación de Reemplazo (M4): Cambiar un evento crítico por un "falso positivo"
    "replace_encryption_with_retention": {
        "category": MutationCategory.STRUCTURAL,
        "factory": lambda: ReplaceEventMutation("encryption_applied", "retention_period_verify")
    },


    # ======================================================
    # TEMPORAL (Nivel 2)
    # ======================================================
    "wrong_position_verify_legal_basis": {
        "category": MutationCategory.TEMPORAL,
        "factory": lambda: WrongPositionMutation("verify_legal_basis")
    },
    "wrong_position_encryption": {
        "category": MutationCategory.TEMPORAL,
        "factory": lambda: WrongPositionMutation("encryption_applied")
    },
    "swap_consent_and_collection": {
        "category": MutationCategory.TEMPORAL,
        "factory": lambda: SwapEventOrderMutation("check_consent", "record_purpose")
    },

    # Mueve 'privacy_notice_disclosed' ANTES de la recolección (Tu regla exige AFTER)
    "swap_collection_and_privacy_notice": {
        "category": MutationCategory.TEMPORAL,
        "factory": lambda: SwapEventOrderMutation("DATA_COLLECTION", "privacy_notice_disclosed")
    },
    # Rompe el orden de los derechos de usuario: responder antes de verificar identidad
    "swap_identity_verification_and_response": {
        "category": MutationCategory.TEMPORAL,
        "factory": lambda: SwapEventOrderMutation("verify_request_identity", "respond_user_right")
    },


    # ======================================================
    # CONTEXTUAL (Nivel 3)
    # ======================================================
    # (Tus mutaciones existentes se mantienen...)
    "change_legal_basis_to_contract": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyLegalBasisMutation("contract")
    },
    "change_data_category_to_standard": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyDataCategoryMutation("DataCategory.STANDARD")
    },
    "change_data_category_to_health": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyDataCategoryMutation("DataCategory.HEALTH")
    },

    # --- NUEVAS CONTEXTUALES BASADAS EN TU VALIDADOR ---
    # Cambia la categoría a SPECIAL para disparar la obligación de access_control_check
    "change_data_category_to_special": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyDataCategoryMutation("DataCategory.SPECIAL")
    },
    # Pone a False los destinatarios externos para evaluar la advertencia DATA_TRANSFER_THIRD_PARTY_FORBIDDEN
    "modify_context_third_party_to_false": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyContextFieldMutation("has_third_party_recipients", False)
    },
    # Fuerza a True los destinatarios externos en una traza limpia para exigir contratos
    "modify_context_third_party_to_true": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyContextFieldMutation("has_third_party_recipients", True)
    },
    # Cambia transferencia internacional a 'third_country' para exigir salvaguardas (DATA_TRANSFER_INTERNATIONAL_REQUIRED)
    "modify_context_international_to_third_country": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyContextFieldMutation("international_transfer", "third_country")
    },
    # Limpia el periodo de retención en el contexto para hacer saltar CASE_END_MISSING_RETENTION_CONTEXT
    "clear_context_retention_period": {
        "category": MutationCategory.CONTEXTUAL,
        "factory": lambda: ModifyContextFieldMutation("retention_period", None)
    },


    # ======================================================
    # SEMANTIC / COMPLIANCE CHAINS (Nivel 4)
    # ======================================================
    
    # Rompe el flujo secuencial inicial: coloca verify_legal_basis DESPUÉS de un DATA_COLLECTION
    "break_initial_compliance_chain": {
        "category": MutationCategory.SEMANTIC,
        "factory": lambda: BreakInitialChainMutation()
    },
    # Modifica el subtipo de derecho de usuario (UserRightType) para dejar los eventos huérfanos de su lógica específica
    # Ej: Un evento de Rectificación al que se le quitan los flujos obligatorios de propagación a réplicas.
    "corrupt_user_right_type_to_erasure": {
        "category": MutationCategory.SEMANTIC,
        "factory": lambda: ModifyUserRightTypeMutation(to_type="UserRightType.ERASURE")
    },
    # Incumplimiento Parcial de Cadena en Eliminación: Mantener record_retention_period pero eliminar la purga real
    "incomplete_deletion_chain": {
        "category": MutationCategory.SEMANTIC,
        "factory": lambda: RemoveEventMutation("erase_data")
    }
}
