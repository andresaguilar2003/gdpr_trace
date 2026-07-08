from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory


class ModifyUserRightTypeMutation(BaseMutation):

    category = MutationCategory.SEMANTIC

    def __init__(self, to_type):
        self.to_type = to_type
        # Formateamos el nombre limpiando posibles rutas del enum para el registro
        clean_type = str(to_type).split(".")[-1].lower()
        self.name = f"corrupt_user_right_type_to_{clean_type}"

    def apply(self, trace):
        # Primero intentamos modificar el atributo directamente en la traza (si tu modelo lo tiene ahí)
        if hasattr(trace, "user_right_type"):
            setattr(trace, "user_right_type", self.to_type)
            
        # También lo modificamos en el contexto por si tu validador lo lee desde trace.context
        if hasattr(trace, "context") and trace.context is not None:
            if hasattr(trace.context, "user_right_type"):
                setattr(trace.context, "user_right_type", self.to_type)
            # En caso de que en el XML viniera mapeado genéricamente como un campo de texto
            elif hasattr(trace.context, "data_subject_type"): 
                # Nota: Ajusta este campo secundario si en tu parser guardas el derecho bajo otra clave
                pass

        return trace