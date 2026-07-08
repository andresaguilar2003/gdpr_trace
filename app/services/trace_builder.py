from app.models.trace import Trace
from app.models.original_event import OriginalEvent
from app.models.gdpr_event import GDPREvent
from app.specifications.activity_gdpr_mapping import ACTIVITY_GDPR_PATTERNS
from app.specifications.event_position import EventPosition
from app.models.user_right_type import UserRightType
from app.models.activity import Activity


IGNORED_KEYS = {
    "concept:name",
    "time:timestamp",
    "lifecycle:transition"
}

def _get_attr(log, trace, key):
    val = trace.attributes.get(key)

    if val is None:
        val = log.attributes.get(key)

    if hasattr(val, "value"):
        return val.value

    if isinstance(val, dict):
        return val.get("value")

    return val

def build_traces_from_pm4py_log(log):

    traces = []

    for case_index, pm_trace in enumerate(log):

        trace = Trace(trace_id=f"case_{case_index}")

        trace_attributes = set(pm_trace.attributes.keys())

        for order, event in enumerate(pm_trace):

            name = event.get("concept:name")
            timestamp = event.get("time:timestamp")
            from app.specifications.activity_types import ActivityType

            activity_type_str = event.get("gdpr:activity_type")

            activity_type = None
            if activity_type_str:
                try:
                    activity_type = ActivityType[activity_type_str]
                except KeyError:
                    activity_type = None

            user_right_type_str = event.get("gdpr:user_right_type")

            user_right_type = None

            if user_right_type_str:

                try:
                    user_right_type = UserRightType[user_right_type_str]
                except KeyError:
                    user_right_type = None
            # -------------------------
            # atributos reales
            # -------------------------
            attributes = {}

            for k, v in event.items():

                if k in IGNORED_KEYS:
                    continue

                if k in trace_attributes:
                    continue

                attributes[k] = v

            # =====================================================
            # GDPR EVENT
            # =====================================================

            if activity_type == ActivityType.GDPR_COMPLIANCE:

                position = None

                for rules in ACTIVITY_GDPR_PATTERNS.values():

                    for rule in rules:

                        if rule["event"] == name:

                            position = rule["position"]
                            break

                    if position is not None:
                        break

                ev = GDPREvent(
                    event_id=f"{case_index}_{order}",
                    name=name,
                    timestamp=timestamp,
                    order=order,
                    position=position,
                )

            # =====================================================
            # ORIGINAL EVENT
            # =====================================================

            else:

                ev = OriginalEvent(
                    event_id=f"{case_index}_{order}",
                    name=name,
                    timestamp=timestamp,
                    order=order,
                    raw_label=name,
                    attributes=attributes
                )

                # 🔥 CRÍTICO para validadores
                ev.activity = Activity(
                    activity_id=f"{case_index}_{order}",
                    label=name,
                    activity_type=activity_type
                )

                ev.activity.user_right_type = user_right_type

                ev.user_right_type = user_right_type

            # 👉 añadir SIEMPRE
            trace.add_event(ev)

        # 👉 añadir trace fuera del loop de eventos
        traces.append(trace)

    return traces