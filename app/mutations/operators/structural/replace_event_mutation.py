from app.mutations.base.base_mutation import BaseMutation
from app.mutations.base.mutation_category import MutationCategory
from app.models.gdpr_event import GDPREvent


class ReplaceEventMutation(BaseMutation):

    category = MutationCategory.STRUCTURAL

    def __init__(self, target_event_name, replacement_event_name):
        self.target_event_name = target_event_name
        self.replacement_event_name = replacement_event_name
        
        # Generamos un nombre descriptivo para identificar qué se reemplazó
        self.name = f"replace_{target_event_name}_with_{replacement_event_name}"

    def apply(self, trace):
        # Iteramos directamente sobre los eventos de la traza
        for event in trace.events:
            if (
                isinstance(event, GDPREvent)
                and event.name == self.target_event_name
            ):
                # Sustituimos el nombre del evento original por el nuevo
                event.name = self.replacement_event_name
                
                # Opcional: Si tu clase GDPREvent tiene un atributo interno que se calcule 
                # a partir del nombre, o si quieres mutar alguna otra propiedad, lo puedes hacer aquí.
                
                # Rompemos el bucle tras el primer reemplazo (comportamiento estándar de mutaciones)
                break

        return trace