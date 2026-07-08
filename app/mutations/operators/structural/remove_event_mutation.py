from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory
from app.models.gdpr_event import GDPREvent


class RemoveEventMutation(BaseMutation):

    def __init__(self, event_name):

        self.event_name = event_name

        self.name = (
            f"remove_{event_name}"
        )

    def apply(self, trace):

        trace.events = [

            event for event in trace.events

            if event.name != self.event_name
        ]

        return trace