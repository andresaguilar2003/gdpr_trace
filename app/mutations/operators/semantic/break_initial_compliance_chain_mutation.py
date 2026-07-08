from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory
from app.models.gdpr_event import GDPREvent


class BreakInitialChainMutation(BaseMutation):

    category = MutationCategory.SEMANTIC
    name = "break_initial_compliance_chain"

    def apply(self, trace):
        # 1. Encontrar y extraer el evento 'verify_legal_basis'
        target_event = None
        for event in trace.events:
            if isinstance(event, GDPREvent) and event.name == "verify_legal_basis":
                target_event = event
                break

        # Si no existe en la traza, no podemos romper la cadena inicial
        if not target_event:
            return trace

        # Lo removemos de su posición original
        trace.events.remove(target_event)

        # 2. Buscar el primer evento 'DATA_COLLECTION' para moverlo justo detrás
        collection_index = -1
        for i, event in enumerate(trace.events):
            if isinstance(event, GDPREvent) and event.name == "DATA_COLLECTION":
                collection_index = i
                break

        if collection_index != -1:
            # Modificamos semánticamente el orden para que sea posterior a la recolección
            target_event.order = trace.events[collection_index].order + 0.1
            # Lo insertamos inmediatamente después
            trace.events.insert(collection_index + 1, target_event)
        else:
            # Si no hay DATA_COLLECTION, simplemente lo mandamos al final de la traza para romper el flujo de inicio
            if trace.events:
                target_event.order = trace.events[-1].order + 1.0
            trace.events.append(target_event)

        return trace
