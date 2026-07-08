from enum import Enum

class ActivityType(Enum):

    CASE_START = "case_start"

    DATA_COLLECTION = "data_collection"

    DATA_ACCESS = "data_access"

    DATA_PROCESSING = "data_processing"

    AUTOMATED_DECISION = "automated_decision"

    DATA_TRANSFER = "data_transfer"

    STORAGE_MANAGEMENT = "storage_management"

    USER_RIGHT_REQUEST = "user_right_request"

    DATA_DELETION = "data_deletion"

    GDPR_COMPLIANCE = "gdpr_compliance"

    CASE_END = "case_end"

    OTHER = "other"