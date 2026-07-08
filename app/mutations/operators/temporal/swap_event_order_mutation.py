from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory


class SwapEventOrderMutation(BaseMutation):

    name = "swap_event_order"
    category = MutationCategory.TEMPORAL

    def __init__(self, first_event_name, second_event_name):
        self.first_event_name = first_event_name
        self.second_event_name = second_event_name

    def apply(self, trace):

        first = None
        second = None

        for e in trace.events:

            if e.name == self.first_event_name and first is None:
                first = e

            elif e.name == self.second_event_name and second is None:
                second = e

        if first and second:
            first.order, second.order = second.order, first.order

        trace.events.sort(key=lambda x: x.order)

        return trace