class ValidationRuleCatalog:

    GENERIC_RULES = {
        "GDPR_COMPLIANCE_REQUIRED",
        "GDPR_REQUIRED",
        "COMPLIANCE_REQUIRED",
        "UNKNOWN_RULE"
    }

    ALIASES = {
        "CASE_START_REQUIRED": "CASE_START_VERIFY_LEGAL_BASIS",
        "LEGAL_BASIS_REQUIRED": "CASE_START_VERIFY_LEGAL_BASIS",
        "DATA_ACCESS_REQUIRED": "DATA_ACCESS_CONTROL_REQUIRED",
        "CONSENT_REQUIRED": "DATA_COLLECTION_CONSENT_REQUIRED",
        "NOTICE_REQUIRED": "DATA_COLLECTION_NOTICE",
        "PURPOSE_REQUIRED": "DATA_COLLECTION_PURPOSE_REQUIRED",
        "MINIMISATION_REQUIRED": "DATA_PROCESSING_MINIMISATION",
        "ENCRYPTION_REQUIRED": "DATA_PROCESSING_ENCRYPTION_REQUIRED",
        "LOG_PROCESSING_REQUIRED": "DATA_PROCESSING_LOG_REQUIRED",
        "RETENTION_REQUIRED": "DATA_DELETION_RETENTION_REQUIRED",
        "ERASURE_REQUIRED": "DATA_DELETION_ERASE_REQUIRED",
        "DISCLOSURE_REQUIRED": "AUTOMATED_DECISION_DISCLOSURE_REQUIRED"
    }

    DEFAULT_MESSAGES = {
        "CASE_START_VERIFY_LEGAL_BASIS":
            "Missing verify_legal_basis after CASE_START.",
        "CASE_START_VERIFY_LEGAL_BASIS_DUPLICATED":
            "verify_legal_basis appears more than once in the trace.",
        "DATA_COLLECTION_NOTICE":
            "Missing or misplaced privacy_notice_disclosed for data collection.",
        "DATA_COLLECTION_CONSENT_REQUIRED":
            "Missing or misplaced check_consent for consent-based data collection.",
        "DATA_COLLECTION_PURPOSE_REQUIRED":
            "Missing record_purpose in a data collection trace.",
        "DATA_COLLECTION_LEGAL_BASIS_FLOW":
            "CASE_START and verify_legal_basis must occur before data collection.",
        "DATA_PROCESSING_MINIMISATION":
            "Missing or misplaced minimisation_check before data processing.",
        "DATA_PROCESSING_ENCRYPTION_REQUIRED":
            "Missing or misplaced encryption_applied for non-standard data.",
        "DATA_PROCESSING_LOG_REQUIRED":
            "Missing log_processing_activity for data processing accountability.",
        "DATA_ACCESS_CONTROL_REQUIRED":
            "Missing access_control_check before sensitive data access.",
        "DATA_TRANSFER_THIRD_PARTY_REQUIRED":
            "Missing check_third_party_agreement before third-party transfer.",
        "DATA_TRANSFER_INTERNATIONAL_REQUIRED":
            "Missing verify_international_safeguard before international transfer.",
        "AUTOMATED_DECISION_DISCLOSURE_REQUIRED":
            "Missing automated_logic_disclosure before automated decision logic.",
        "USER_RIGHT_REQUEST_RESPONSE_REQUIRED":
            "Missing respond_user_right after a user rights request.",
        "USER_RIGHT_IDENTITY_VERIFICATION":
            "Missing verify_request_identity before handling a user rights request.",
        "DATA_DELETION_RETENTION_REQUIRED":
            "Missing record_retention_period before data deletion.",
        "DATA_DELETION_ERASE_REQUIRED":
            "Missing erase_data after a data deletion request.",
        "CASE_END_RETENTION_VERIFY":
            "Missing retention_period_verify before CASE_END.",
        "CASE_END_ERASURE":
            "Missing confirm_data_erasure before CASE_END.",
        "CASE_END_MISSING_RETENTION_CONTEXT":
            "Missing retention_period in the trace context."
    }

    DEFAULT_RECOMMENDATIONS = {
        "CASE_START_VERIFY_LEGAL_BASIS":
            "Inject verify_legal_basis immediately after CASE_START.",
        "CASE_START_VERIFY_LEGAL_BASIS_DUPLICATED":
            "Keep exactly one verify_legal_basis event per trace.",
        "DATA_COLLECTION_NOTICE":
            "Inject or move privacy_notice_disclosed after the data collection activity.",
        "DATA_COLLECTION_CONSENT_REQUIRED":
            "Inject or move check_consent before the data collection activity.",
        "DATA_COLLECTION_PURPOSE_REQUIRED":
            "Inject record_purpose in the trace.",
        "DATA_COLLECTION_LEGAL_BASIS_FLOW":
            "Reorder the trace so CASE_START and verify_legal_basis occur before data collection.",
        "DATA_PROCESSING_MINIMISATION":
            "Inject or move minimisation_check before data processing.",
        "DATA_PROCESSING_ENCRYPTION_REQUIRED":
            "Inject or move encryption_applied before processing non-standard data.",
        "DATA_PROCESSING_LOG_REQUIRED":
            "Inject log_processing_activity to demonstrate accountability.",
        "DATA_ACCESS_CONTROL_REQUIRED":
            "Inject access_control_check before exposing sensitive data.",
        "DATA_TRANSFER_THIRD_PARTY_REQUIRED":
            "Inject check_third_party_agreement before the transfer activity.",
        "DATA_TRANSFER_INTERNATIONAL_REQUIRED":
            "Inject verify_international_safeguard before the international transfer.",
        "AUTOMATED_DECISION_DISCLOSURE_REQUIRED":
            "Inject automated_logic_disclosure before automated decision logic.",
        "USER_RIGHT_REQUEST_RESPONSE_REQUIRED":
            "Inject respond_user_right after the user rights request.",
        "USER_RIGHT_IDENTITY_VERIFICATION":
            "Inject verify_request_identity before the user rights request.",
        "DATA_DELETION_RETENTION_REQUIRED":
            "Inject record_retention_period before deletion.",
        "DATA_DELETION_ERASE_REQUIRED":
            "Inject erase_data after the deletion request.",
        "CASE_END_RETENTION_VERIFY":
            "Inject retention_period_verify before CASE_END.",
        "CASE_END_ERASURE":
            "Inject confirm_data_erasure before CASE_END.",
        "CASE_END_MISSING_RETENTION_CONTEXT":
            "Configure retention_period in the GDPR trace context."
    }

    @classmethod
    def normalize_rule(cls, rule):
        if not rule:
            return "UNKNOWN_RULE"

        clean_rule = str(rule).strip()

        if "@" in clean_rule:
            clean_rule = clean_rule.split("@")[-1].strip()

        return cls.ALIASES.get(clean_rule, clean_rule)

    @classmethod
    def is_generic(cls, rule):
        normalized = cls.normalize_rule(rule)

        return normalized in cls.GENERIC_RULES

    @classmethod
    def enrich_issue(cls, issue, issue_type="violation"):
        rule = cls.normalize_rule(issue.get("rule"))
        event = issue.get("event", "trace")

        return {
            "rule": rule,
            "event": event,
            "message": issue.get(
                "message",
                cls.DEFAULT_MESSAGES.get(
                    rule,
                    f"T5 predicted GDPR {issue_type}: {rule}"
                )
            ),
            "recommendation": issue.get(
                "recommendation",
                cls.DEFAULT_RECOMMENDATIONS.get(
                    rule,
                    "Review the trace against the deterministic GDPR rule set and add more training examples for this pattern."
                )
            )
        }
