from copy import deepcopy

from app.mutations.base.base_mutation import BaseMutation
from app.models.gdpr_event import GDPREvent


class DuplicateEventMutation(BaseMutation):

    name = "duplicate_event"

    def __init__(self, target_event_name):

        self.target_event_name = target_event_name

    def apply(self, trace):

        for i, event in enumerate(trace.events):

            if (
                isinstance(event, GDPREvent)
                and event.name == self.target_event_name
            ):

                duplicated = deepcopy(event)

                duplicated.order = event.order + 0.1

                trace.events.insert(i + 1, duplicated)
                break

        return trace