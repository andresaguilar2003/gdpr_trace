import copy

from app.models.mutation_result import MutationResult
from app.mutations.reports.mutation_report import MutationReport
from app.mutations.reports.mutation_trace_report import MutationTraceReport
from app.mutations.services.trace_mutation_normalizer import TraceMutationNormalizer


class MutationEngine:

    def __init__(self, validator):
        self.validator = validator

    def apply_mutations(
        self,
        traces,
        mutation_plan
    ):
        report = MutationReport()
        mutated_traces = []

        for trace in traces:
            trace_id = trace.trace_id
            applicable_mutations = mutation_plan.get_mutations_for_trace(trace_id)

            mutated_trace = copy.deepcopy(trace)

            for mutation in applicable_mutations:
                mutated_trace = mutation.apply(mutated_trace)

                TraceMutationNormalizer.normalize(mutated_trace)

                # Ejecutamos la validación
                validation = self.validator.validate(mutated_trace)

                violations = validation.get("violations", [])
                warnings = validation.get("warnings", [])

                # 1. Determinar severidad
                severity = self._severity_from_validation(
                    validation,
                    violations,
                    warnings
                )

                # =====================================================
                # 🌟 DINÁMICO: CONSTRUIR RECOMENDACIÓN DETALLADA
                # =====================================================
                # Recopilamos todas las recomendaciones específicas dictadas por el validador
                specific_recommendations = []
                
                for v in violations:
                    if "recommendation" in v:
                        specific_recommendations.append(f"• [Violation - {v['rule']}]: {v['recommendation']}")
                
                for w in warnings:
                    if "recommendation" in w:
                        specific_recommendations.append(f"• [Warning - {w['rule']}]: {w['recommendation']}")

                if specific_recommendations:
                    # Unimos todas las recomendaciones encontradas separadas por saltos de línea
                    recommendation = "Action Required:\n" + "\n".join(specific_recommendations)
                else:
                    recommendation = "No privacy issues detected. The trace complies with the established GDPR rules."

                # 2. Guardamos el reporte detallado
                result = MutationTraceReport(
                    trace_id=trace_id,
                    mutation_name=mutation.name,
                    validator_result=validation,
                    severity=severity,
                    recommendation=recommendation  # Ya no es un texto genérico fijo
                )
            
                report.add_result(result)

            mutated_traces.append(mutated_trace)

        return mutated_traces, report

    @staticmethod
    def _severity_from_validation(validation, violations, warnings):
        impact = validation.get("impact")

        if not impact and validation.get("ai_result"):
            impact = validation["ai_result"].get("impact")

        if impact in {"0", "0_COMPLIANT"}:
            return "COMPLIANT"

        if impact in {"1", "1_VIOLATION"}:
            return "VIOLATION"

        if impact in {"2", "2_WARNING"}:
            return "WARNING"

        return (
            "VIOLATION" if violations
            else "WARNING" if warnings
            else "COMPLIANT"
        )
