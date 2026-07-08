from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory

class ModifyContextFieldMutation(BaseMutation):

    category = MutationCategory.CONTEXTUAL

    def __init__(self, attribute_name, new_value):
        self.attribute_name = attribute_name
        self.new_value = new_value
        self.name = f"modify_context_{attribute_name}_to_{str(new_value).lower()}"

    def apply(self, trace):
        # Modificamos el objeto de contexto que cuelga de tu objeto Trace de dominio
        if hasattr(trace, "context") and trace.context is not None:
            setattr(trace.context, self.attribute_name, self.new_value)
        return trace
