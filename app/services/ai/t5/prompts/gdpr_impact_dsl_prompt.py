import json

from app.services.ai.t5.serializers.ai_trace_serializer import AITraceSerializer
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog


class GDPRImpactDSLPromptBuilder:
    """Builds compact T5 prompts for rule-level GDPR impact prediction."""

    IMPACT_PREFIX = "validate gdpr impact:"

    @staticmethod
    def build(trace, rule_label="COMPLIANCE_CHECK"):
        trace_json = json.loads(AITraceSerializer.serialize(trace))
        return GDPRImpactDSLPromptBuilder.build_from_trace_json(
            trace_json,
            rule_label=rule_label,
        )

    @staticmethod
    def build_from_trace_json(trace_json, rule_label="COMPLIANCE_CHECK"):
        context = trace_json.get("context", {})
        events = trace_json.get("events", [])
        rule_group = GDPRImpactDSLPromptBuilder.simplify_rule_name(rule_label)
        context_bits = [
            f"legal_basis:{GDPRImpactDSLPromptBuilder.compact_value(context.get('legalBasis'))}",
            f"data_category:{GDPRImpactDSLPromptBuilder.compact_value(context.get('dataCategory'))}",
            f"retention:{GDPRImpactDSLPromptBuilder.compact_value(context.get('retentionPeriod'))}",
            f"third_party:{GDPRImpactDSLPromptBuilder.compact_value(context.get('hasThirdPartyRecipients'))}",
            f"international:{GDPRImpactDSLPromptBuilder.compact_value(context.get('internationalTransfer'))}",
            f"safeguard:{GDPRImpactDSLPromptBuilder.compact_value(context.get('transferSafeguard'))}",
            f"consent:{GDPRImpactDSLPromptBuilder.compact_value(context.get('consentStatus'))}",
        ]
        include_timestamps = any(
            token in ValidationRuleCatalog.normalize_rule(rule_label)
            for token in [
                "RETENTION",
                "ERASURE",
                "CASE_END",
                "ORDER",
                "FLOW",
                "POSITION",
            ]
        )
        trace_parts = []

        for event in events:
            activity_type = event.get("activityType")
            name = event.get("name")
            position = event.get("position")
            event_token = GDPRImpactDSLPromptBuilder.compact_value(activity_type or name)

            if position not in {None, "None", "none"}:
                event_token = (
                    f"{event_token}"
                    f"[{GDPRImpactDSLPromptBuilder.compact_value(position)}]"
                )

            if include_timestamps and event.get("timestamp"):
                event_token = f"{event_token}({event['timestamp']})"

            trace_parts.append(event_token)

        return (
            f"{GDPRImpactDSLPromptBuilder.IMPACT_PREFIX} "
            f"rule: {rule_group} | "
            f"context: {'; '.join(context_bits)} | "
            f"trace: {' -> '.join(trace_parts)} | "
            "return only 0, 1 or 2"
        )

    @staticmethod
    def compact_value(value):
        if value is None:
            return "none"

        if isinstance(value, bool):
            return str(value).lower()

        return str(value).replace(" ", "_")

    @staticmethod
    def simplify_rule_name(rule_label):
        rule = ValidationRuleCatalog.normalize_rule(rule_label)

        if rule == "COMPLIANT":
            return "COMPLIANCE_CHECK"

        families = [
            "CASE_START",
            "CASE_END",
            "DATA_COLLECTION",
            "DATA_PROCESSING",
            "DATA_ACCESS",
            "DATA_TRANSFER",
            "AUTOMATED_DECISION",
            "USER_RIGHT",
            "DATA_DELETION",
        ]

        for family in families:
            if rule.startswith(family):
                return family

        return rule
