from app.models.user_right_type import UserRightType
from app.specifications.activity_types import ActivityType
from app.specifications.event_position import EventPosition
from app.specifications.data_categories import DataCategory


ACTIVITY_GDPR_PATTERNS = {

    ActivityType.CASE_START: [

        {
            "event": "verify_legal_basis",
            "position": EventPosition.AFTER,
            "condition": lambda ctx, ev: True
        }

    ],

    ActivityType.DATA_COLLECTION: [

        {
            "event": "check_consent",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.legal_basis == "consent"
        },

        {
            "event": "privacy_notice_disclosed",
            "position": EventPosition.AFTER,
            "condition": lambda ctx, ev: True
        },

        {
            "event": "record_purpose",
            "position": EventPosition.BEFORE,  # o AFTER → da igual para “related”
            "condition": lambda ctx, ev: True
        }
    ],

    ActivityType.DATA_ACCESS: [

        {
            "event": "access_control_check",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.data_category in [
                DataCategory.HEALTH,
                DataCategory.SPECIAL
            ]
        }

    ],

    ActivityType.DATA_PROCESSING: [

        {
            "event": "minimisation_check",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: True
        },

        {
            "event": "encryption_applied",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.data_category != DataCategory.STANDARD
        },

        {
            "event": "log_processing_activity",
            "position": EventPosition.AFTER,
            "condition": lambda ctx, ev: True
        }

    ],

    ActivityType.DATA_TRANSFER: [

        {
            "event": "check_third_party_agreement",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.has_third_party_recipients
        },

        {
            "event": "verify_international_safeguard",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.international_transfer == "third_country"
        }

    ],

    ActivityType.AUTOMATED_DECISION: [

        {
            "event": "automated_logic_disclosure",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: True
        }

    ],

    ActivityType.USER_RIGHT_REQUEST: [

        # ---------------------------------
        # GENERIC USER RIGHT EVENTS
        # ---------------------------------

        {
            "event": "verify_request_identity",
            "position": EventPosition.BEFORE,
            "priority": 0,
            "condition": lambda ctx, ev: True
        },

        {
            "event": "respond_user_right",
            "position": EventPosition.AFTER,
            "priority": 999,
            "condition": lambda ctx, ev: True
        },


        # ---------------------------------
        # ACCESS RIGHT
        # ---------------------------------


        {
            "event": "provide_data_copy",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.ACCESS
        },

        # ---------------------------------
        # RECTIFICATION RIGHT (Art. 16)
        # ---------------------------------

        {
            "event": "update_primary_record",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.RECTIFICATION
        },

        {
            "event": "propagate_rectification_to_replicas",
            "position": EventPosition.AFTER,
            "priority": 20,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.RECTIFICATION
        },

        {
            "event": "notify_data_rectification_to_recipients",
            "position": EventPosition.AFTER,
            "priority": 30,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.RECTIFICATION
        },

        {
            "event": "verify_rectification_consistency",
            "position": EventPosition.AFTER,
            "priority": 40,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.RECTIFICATION
        },

        # ---------------------------------
        # ERASURE RIGHT / OLVIDO (Art. 17)
        # ---------------------------------

        {
            "event": "erase_primary_record",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.ERASURE
        },

        {
            "event": "propagate_erasure_to_replicas",
            "position": EventPosition.AFTER,
            "priority": 20,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.ERASURE
        },

        {
            "event": "notify_third_party_deletion",
            "position": EventPosition.AFTER,
            "priority": 30,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.ERASURE
        },

        {
            "event": "verify_erasure_completion",
            "position": EventPosition.AFTER,
            "priority": 40,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None)
                == UserRightType.ERASURE
        },

        # ---------------------------------
        # RESTRICTION OF PROCESSING (Art. 18)
        # ---------------------------------
        {
            "event": "mark_data_as_restricted",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.RESTRICTION
        },
        {
            "event": "verify_restriction_lift_conditions",
            "position": EventPosition.BEFORE,
            "priority": 20,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.RESTRICTION
        },

        # ---------------------------------
        # PORTABILITY RIGHT (Art. 20)
        # ---------------------------------
        {
            "event": "generate_interoperable_format",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.PORTABILITY
        },
        {
            "event": "transmit_data_to_new_controller",
            "position": EventPosition.AFTER,
            "priority": 20,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.PORTABILITY
        },

        # ---------------------------------
        # OBJECTION RIGHT (Art. 21)
        # ---------------------------------
        {
            "event": "halt_processing_activities",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.OBJECTION
        },
        {
            "event": "verify_compelling_legitimate_grounds",
            "position": EventPosition.BEFORE,
            "priority": 20,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.OBJECTION
        },

        # ---------------------------------
        # AUTOMATED DECISION REVIEW (Art. 22)
        # ---------------------------------

        {
            "event": "contest_automated_decision",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.AUTOMATED_DECISION_REVIEW
        },

        # ---------------------------------
        # INFORMATION RIGHT (Art. 13-14)
        # ---------------------------------
        {
            "event": "provide_transparency_details",
            "position": EventPosition.AFTER,
            "priority": 10,
            "condition": lambda ctx, ev:
                getattr(ev, "user_right_type", None) == UserRightType.INFORMATION
        }

    ],

    ActivityType.DATA_DELETION: [

        {
            "event": "record_retention_period",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: True
        },

        {
            "event": "erase_data",
            "position": EventPosition.AFTER,
            "condition": lambda ctx, ev: True
        }

    ],

    ActivityType.CASE_END: [

        {
            "event": "retention_period_verify",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: True
        },

        {
            "event": "confirm_data_erasure",
            "position": EventPosition.BEFORE,
            "condition": lambda ctx, ev: ctx.retention_period is not None
        }

    ],

    ActivityType.OTHER: []

}