class MutationReport:

    def __init__(self):

        self.total_traces = 0

        self.total_mutated_traces = 0

        self.total_violations = 0

        self.total_warnings = 0

        self.mutations = []

        self.trace_reports = []


    def add_result(self, result):

        self.trace_reports.append(result)

        violations = len(
            result.validator_result["violations"]
        )

        warnings = len(
            result.validator_result["warnings"]
        )

        self.total_violations += violations
        self.total_warnings += warnings

        self.total_mutated_traces += 1