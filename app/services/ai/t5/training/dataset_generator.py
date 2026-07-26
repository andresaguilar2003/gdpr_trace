from app.services.ai.t5.training.dataset_example import (
    DatasetExample
)

from app.services.ai.t5.serializers.ai_trace_serializer import (
    AITraceSerializer
)
from app.services.ai.t5.prompts.gdpr_validation_prompt import (
    GDPRValidationPromptBuilder
)


class DatasetGenerator:

    @staticmethod
    def build_input_text(trace):
        return GDPRValidationPromptBuilder.build(
            AITraceSerializer.serialize(trace)
        )

    @staticmethod
    def build_target_text(validation_result):
        violations = validation_result.get("violations", [])
        warnings = validation_result.get("warnings", [])

        status = (
            "valid"
            if len(violations) == 0
            else "invalid"
        )

        violation_labels = [
            DatasetGenerator._format_issue(violation)
            for violation in violations
        ]

        warning_labels = [
            DatasetGenerator._format_issue(warning)
            for warning in warnings
        ]

        return (
            f"{status} | violations: "
            f"{DatasetGenerator._join_labels(violation_labels)}"
            f" | warnings: "
            f"{DatasetGenerator._join_labels(warning_labels)}"
        )

    @staticmethod
    def _format_issue(issue):
        rule = issue.get("rule", "UNKNOWN_RULE")
        event = issue.get("event", "trace")

        return f"{rule}@{event}"

    @staticmethod
    def _join_labels(labels):
        if not labels:
            return "none"

        return "; ".join(labels)

    @staticmethod
    def build_example(trace, validation_result):
        return DatasetExample(
            input_text=DatasetGenerator.build_input_text(trace),
            target_text=DatasetGenerator.build_target_text(validation_result)
        )

    @staticmethod
    def build_violation_example(trace, violation):
        validation_result = {
            "violations": [violation],
            "warnings": []
        }

        return DatasetGenerator.build_example(
            trace,
            validation_result
        )
