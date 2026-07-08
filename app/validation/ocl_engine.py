from app.validation.validators.gdpr_enrichment_validator import GDPREnrichmentValidator


class OCLEngine:

    def validate_trace(self, trace):
        """
        Ejecuta todas las reglas OCL sobre una traza enriquecida.
        """

        violations = []
        warnings = []

        # =====================================================
        # GDPR ENRICHMENT RULES
        # =====================================================

        result = GDPREnrichmentValidator.validate(trace)

        violations.extend(result["violations"])
        warnings.extend(result["warnings"])


        return {
            "violations": violations,
            "warnings": warnings
        }

    # =====================================================
    # VALIDATE MULTIPLE TRACES
    # =====================================================

    def validate_traces(self, traces):

        all_results = {}

        for trace in traces:

            result = self.validate_trace(trace)

            if result["violations"] or result["warnings"]:

                all_results[trace.trace_id] = result

        return all_results