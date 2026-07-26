import json


class GDPRValidationPromptBuilder:

    @staticmethod
    def build(trace_json):
        try:
            trace_json = json.dumps(
                json.loads(trace_json),
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        except (TypeError, ValueError):
            trace_json = str(trace_json).strip()

        return (
            "validate gdpr enrichment: "
            + trace_json
        )
