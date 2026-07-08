from app.services.ai.t5.serializers.ai_trace_serializer import (
    AITraceSerializer
)

from app.services.ai.t5.prompts.gdpr_validation_prompt import (
    GDPRValidationPromptBuilder
)
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog

class AIGDPRValidator:

    def __init__(self, llm):

        self.llm = llm

    def validate(self, trace):

        trace_json = (
            AITraceSerializer.serialize(
                trace
            )
        )

        prompt = (
            GDPRValidationPromptBuilder.build(
                trace_json
            )
        )

        response = self.llm.generate(
            prompt
        )

        return self._parse_response(response)

    @staticmethod
    def _parse_response(response):
        parts = [
            part.strip()
            for part in response.split("|")
        ]

        status = parts[0].lower() if parts else ""

        result = {
            "isValid": status.startswith("valid"),
            "violations": [],
            "warnings": [],
            "rawResponse": response
        }

        if not (
            status.startswith("valid")
            or status.startswith("invalid")
        ):
            result["parseError"] = "Model did not return compact validation format."
            return result

        result["isValid"] = status.startswith("valid")

        for part in parts[1:]:
            lower_part = part.lower()

            if lower_part.startswith("violations:"):
                result["violations"] = AIGDPRValidator._parse_issues(
                    part.split(":", 1)[1]
                )

            if lower_part.startswith("warnings:"):
                result["warnings"] = AIGDPRValidator._parse_issues(
                    part.split(":", 1)[1]
                )

        return result

    @staticmethod
    def _parse_issues(raw_issues):
        raw_issues = raw_issues.strip()

        if raw_issues.lower() == "none":
            return []

        issues = []

        for raw_issue in raw_issues.split(";"):
            raw_issue = raw_issue.strip()

            if not raw_issue:
                continue

            if "@" in raw_issue:
                rule, event = raw_issue.rsplit("@", 1)
            else:
                rule = raw_issue
                event = "trace"

            issues.append({
                "rule": ValidationRuleCatalog.normalize_rule(rule.strip()),
                "event": event.strip()
            })

        return issues
