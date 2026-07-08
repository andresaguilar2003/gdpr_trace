from app.mutations.base.base_mutation import BaseMutation

class ModifyDataCategoryMutation(BaseMutation):

    name = "modify_data_category"

    def __init__(self, new_category):
        self.new_category = new_category

    def apply(self, trace):
        if hasattr(trace, "context") and trace.context is not None:
            trace.context.data_category = self.new_category
        return trace