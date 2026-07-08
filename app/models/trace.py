from app.models.context import Context


class Trace:

    def __init__(self, trace_id, source=None, context=None):

        self.trace_id = trace_id

        self.source = source

        self.events = []

        # contexto GDPR inferido por LLM
        self.context = context or Context()

        self.is_enriched = False

        self.is_compliant = None

    def add_event(self, event):

        self.events.append(event)

    def get_event_names(self):

        return [e.name for e in self.events]

    def get_attributes(self):

        attributes = set()

        for event in self.events:

            attributes.update(event.attributes.keys())

        return list(attributes)

    def sort_events(self):

        self.events.sort(key=lambda e: e.order)

    def __repr__(self):

        return f"Trace(id={self.trace_id}, events={len(self.events)})"