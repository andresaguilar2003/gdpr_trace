class GDPRValidationPromptBuilder:

    @staticmethod
    def build(trace_json):

        return (
            "validate gdpr enrichment: "
            + trace_json
        )
