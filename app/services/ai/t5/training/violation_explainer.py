class ViolationExplainer:

    MAPPING = {

        "DATA_COLLECTION_CONSENT_REQUIRED": {
            "rationale":
                "The activity collects personal data but no consent verification event was found beforehand.",

            "recommendation":
                "Insert a check_consent event before the data collection activity."
        },

        "DATA_PROCESSING_MINIMISATION": {
            "rationale":
                "Data processing occurred without a prior minimisation check.",

            "recommendation":
                "Add a minimisation_check event before processing."
        },

        "DATA_ACCESS_CONTROL_REQUIRED": {
            "rationale":
                "Sensitive data was accessed without access control verification.",

            "recommendation":
                "Insert access_control_check before the access activity."
        }

    }

    @classmethod
    def explain(cls, rule):

        return cls.MAPPING.get(
            rule,
            {
                "rationale":
                    "A GDPR compliance rule was violated.",

                "recommendation":
                    "Review the trace and restore the required GDPR event."
            }
        )