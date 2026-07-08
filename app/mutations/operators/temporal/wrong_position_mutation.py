from app.mutations.base.base_mutation import BaseMutation
from app.specifications.event_position import EventPosition


class WrongPositionMutation(BaseMutation):

    name = "wrong_position"

    def __init__(self, target_event_name):

        self.target_event_name = target_event_name

    def apply(self, trace):

        for event in trace.events:

            if getattr(event, "name", None) == self.target_event_name:

                if event.position == EventPosition.BEFORE:
                    event.position = EventPosition.AFTER

                elif event.position == EventPosition.AFTER:
                    event.position = EventPosition.BEFORE

        return trace