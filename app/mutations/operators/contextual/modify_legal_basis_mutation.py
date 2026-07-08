from app.mutations.base.base_mutation import BaseMutation

class ModifyLegalBasisMutation(BaseMutation):

    name = "modify_legal_basis"

    def __init__(self, new_legal_basis):
        self.new_legal_basis = new_legal_basis

    def apply(self, trace):
        # Mutar objeto en memoria
        if hasattr(trace, "context") and trace.context is not None:
            trace.context.legal_basis = self.new_legal_basis

        # Mutar para la exportación XML
        xml_key = "gdpr:legal_basis"
        xml_value = str(self.new_legal_basis)

        if hasattr(trace, "attributes") and isinstance(trace.attributes, dict):
            trace.attributes[xml_key] = xml_value

        if hasattr(trace, "log") and trace.log is not None:
            if hasattr(trace.log, "attributes") and isinstance(trace.log.attributes, dict):
                trace.log.attributes[xml_key] = xml_value

        return trace
