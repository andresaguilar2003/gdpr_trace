from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory


class RemoveContextAttributeMutation(BaseMutation):

    name = "remove_context_attribute"
    category = MutationCategory.CONTEXTUAL

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def apply(self, trace):

        if hasattr(trace.context, self.attribute_name):
            setattr(trace.context, self.attribute_name, None)

        return trace