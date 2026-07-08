from app.specifications.activity_types import ActivityType
from app.models.user_right_type import UserRightType


class Activity:

    def __init__(
        self,
        activity_id: str,
        label: str,
        activity_type: ActivityType,
        user_right_type: UserRightType = None
    ):

        self.activity_id = activity_id
        self.label = label
        self.type = activity_type
        self.user_right_type = user_right_type

    def is_type(self, activity_type: ActivityType):

        return self.type == activity_type

    def __repr__(self):

        return (
            f"Activity("
            f"id={self.activity_id}, "
            f"label={self.label}, "
            f"type={self.type}, "
            f"user_right_type={self.user_right_type}"
            f")"
        )