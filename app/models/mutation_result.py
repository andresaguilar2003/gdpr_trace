class MutationResult:

    def __init__(
        self,
        mutation_name,
        trace_id,
        validator_result,
        mutated_trace
    ):
        self.mutation_name = mutation_name
        self.trace_id = trace_id
        self.validator_result = validator_result
        self.mutated_trace = mutated_trace