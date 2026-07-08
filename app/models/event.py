from app.models.activity import Activity


class Event:

    def __init__(
        self,
        event_id,
        name,
        timestamp,
        order,
        activity: Activity = None,
        attributes=None
    ):

        self.event_id = event_id
        self.name = name
        self.timestamp = timestamp
        self.order = order

        # actividad clasificada
        self.activity = activity

        # atributos del XES
        self.attributes = attributes or {}

        # anotación GDPR
        self.gdpr_annotation = None

    def set_activity(self, activity: Activity):

        self.activity = activity

    def set_gdpr_annotation(self, annotation):

        self.gdpr_annotation = annotation

    def get_attribute(self, key, default=None):

        return self.attributes.get(key, default)

    def __repr__(self):

        return f"Event(name={self.name}, order={self.order})"   