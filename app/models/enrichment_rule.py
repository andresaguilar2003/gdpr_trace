from app.specifications.event_position import EventPosition


class EnrichmentRule:

    def __init__(
        self,
        rule_id,
        name,
        description,
        position: EventPosition,
        is_mandatory=True,
        condition=None
    ):

        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.position = position
        self.is_mandatory = is_mandatory
        self.condition = condition

    def applies(self, context):

        if self.condition is None:
            return True

        return self.condition(context)