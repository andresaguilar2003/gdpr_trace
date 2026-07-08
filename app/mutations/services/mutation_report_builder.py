from app.mutations.reports.mutation_report import MutationReport
from app.mutations.reports.mutation_trace_report import (
    MutationTraceReport
)

from app.validation.validators.gdpr_enrichment_validator import (
    GDPREnrichmentValidator
)


class MutationReportBuilder:

    @staticmethod
    def build(log, mutation_configs):

        report = MutationReport()

        report.total_traces = len(log.traces)

        affected_traces = set()

        # =====================================================
        # RECORRER CONFIGURACIONES
        # =====================================================

        for config in mutation_configs:

            mutation_name = config["mutation"]

            start = config["start"]
            end = config["end"]

            report.mutations.append({
                "mutation": mutation_name,
                "start_trace": start,
                "end_trace": end
            })

            # =================================================
            # VALIDAR TRAZAS AFECTADAS
            # =================================================

            for idx in range(start, end + 1):

                if idx >= len(log.traces):
                    continue

                affected_traces.add(idx)

                trace = log.traces[idx]

                validation_result = (
                    GDPREnrichmentValidator.validate(trace)
                )

                violations = validation_result["violations"]
                warnings = validation_result["warnings"]

                severity = (
                    "VIOLATION"
                    if violations
                    else "WARNING"
                    if warnings
                    else "OK"
                )

                recommendation = (
                    MutationReportBuilder
                    ._generate_recommendation(
                        mutation_name,
                        violations,
                        warnings
                    )
                )

                trace_report = MutationTraceReport(
                    trace_id=idx,
                    mutation_name=mutation_name,
                    validator_result=validation_result,
                    severity=severity,
                    recommendation=recommendation
                )

                report.trace_reports.append(trace_report)

                report.total_violations += len(violations)
                report.total_warnings += len(warnings)

        report.total_mutated_traces = len(affected_traces)

        return report

    # =====================================================
    # RECOMMENDATION ENGINE
    # =====================================================

    @staticmethod
    def _generate_recommendation(
        mutation_name,
        violations,
        warnings
    ):

        if violations:

            return (
                f"Critical GDPR compliance issue caused by "
                f"mutation '{mutation_name}'. "
                f"Review missing or incorrectly positioned "
                f"GDPR events."
            )

        if warnings:

            return (
                f"Potential GDPR inconsistency caused by "
                f"mutation '{mutation_name}'. "
                f"Review contextual correctness."
            )

        return "No issues detected."