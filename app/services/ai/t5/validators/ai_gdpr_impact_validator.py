from app.services.ai.t5.prompts.gdpr_impact_dsl_prompt import (
    GDPRImpactDSLPromptBuilder,
)
from app.services.ai.t5.validation_rule_catalog import ValidationRuleCatalog
from app.services.ai.t5.validators.impact_parser import (
    impact_to_status,
    parse_impact_response,
)


class AIGDPRImpactValidator:
    """T5 validator for the simplified DSL -> 0/1/2 impact contract."""

    def __init__(self, llm):
        self.llm = llm

    def validate(self, trace, rule_label="COMPLIANCE_CHECK"):
        prompt = GDPRImpactDSLPromptBuilder.build(
            trace,
            rule_label=rule_label,
        )
        response = self.llm.generate(
            prompt,
            max_output_length=8,
        )
        impact = parse_impact_response(response)
        status = impact_to_status(impact)
        result = {
            "isValid": impact == "0_COMPLIANT",
            "impact": impact,
            "status": status,
            "violations": [],
            "warnings": [],
            "rawResponse": response,
            "inputText": prompt,
            "ruleEvaluated": ValidationRuleCatalog.normalize_rule(rule_label),
        }

        if impact == "PARSE_ERROR":
            result["parseError"] = "Model did not return a numeric 0/1/2 impact."

        return result
