import pm4py


def load_log(path):

    log = pm4py.read_xes(path)

    traces = []

    # CASO 1: pm4py devuelve DataFrame
    if hasattr(log, "groupby"):

        grouped = log.groupby("case:concept:name")

        for case_id, group in grouped:
            group = group.sort_values("time:timestamp")

            events = list(zip(group["concept:name"], group["time:timestamp"]))
            traces.append(events)

    # CASO 2: EventLog clásico
    else:

        for trace in log:

            events = []

            for event in trace:
                events.append(event["concept:name"])

            traces.append(events)

    return traces