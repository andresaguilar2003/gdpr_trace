import statistics


class ProcessMetrics:

    @staticmethod
    def compute(log):

        total_cases = len(log)

        total_events = 0
        activities = set()
        trace_lengths = []
        variants = set()

        for trace in log:

            trace_activities = []

            for event in trace:

                # soporte para pm4py Event
                if isinstance(event, dict):

                    act = event.get("concept:name")

                # soporte para trazas simplificadas
                else:

                    act = str(event)

                if act:
                    activities.add(act)
                    trace_activities.append(act)

                total_events += 1

            trace_lengths.append(len(trace))

            variants.add(tuple(trace_activities))

        avg_trace_length = 0

        if trace_lengths:
            avg_trace_length = statistics.mean(trace_lengths)

        return {
            "cases": total_cases,
            "events": total_events,
            "activities": len(activities),
            "variants": len(variants),
            "avg_trace_length": round(avg_trace_length, 2)
        }