class OriginalEvent:

    def __init__(
        self,
        event_id,
        name,
        timestamp,
        order,
        raw_label,
        attributes=None
    ):

        self.event_id = event_id
        self.name = name
        self.timestamp = timestamp
        self.order = order
        self.raw_label = raw_label

        self.attributes = attributes or {}

        # actividad GDPR
        self.activity = None

        # anotación GDPR
        self.gdpr_annotation = None

    # -----------------------------

    def set_activity(self, activity):

        self.activity = activity

    def set_gdpr_annotation(self, annotation):

        self.gdpr_annotation = annotation

    def get_attribute(self, key, default=None):

        return self.attributes.get(key, default)

    def __repr__(self):

        return f"OriginalEvent(name={self.name}, order={self.order})"