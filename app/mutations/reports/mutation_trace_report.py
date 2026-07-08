class MutationTraceReport:

    def __init__(
        self,
        trace_id,
        mutation_name,
        validator_result,
        severity,
        recommendation
    ):

        self.trace_id = trace_id

        self.mutation_name = mutation_name

        self.validator_result = validator_result

        self.severity = severity

        self.recommendation = recommendation