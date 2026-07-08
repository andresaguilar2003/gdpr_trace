from app.models.event import Event

from app.specifications.event_position import EventPosition


class GDPREvent(Event):

    def __init__(
        self,
        event_id,
        name,
        timestamp,
        order,
        position: EventPosition,
        activity_type=None,
        activity=None
    ):
        super().__init__(event_id, name, timestamp, order, activity)

        self.position = position
        self.activity_type = activity_type