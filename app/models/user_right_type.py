from enum import Enum


class UserRightType(Enum):

    ACCESS = "access"

    RECTIFICATION = "rectification"

    ERASURE = "erasure"

    RESTRICTION = "restriction"

    PORTABILITY = "portability"

    OBJECTION = "objection"

    AUTOMATED_DECISION_REVIEW = "automated_decision_review"

    INFORMATION = "information"

    UNKNOWN = "unknown"