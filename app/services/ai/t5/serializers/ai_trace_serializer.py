import json


class AITraceSerializer:

    @staticmethod
    def serialize(trace):
        def clean(value):
            if value is None:
                return None

            if hasattr(value, "name"):
                return value.name

            return str(value)

        def activity_type(event):
            if hasattr(event, "activity_type") and event.activity_type:
                return clean(event.activity_type)

            activity = getattr(event, "activity", None)

            if activity and getattr(activity, "type", None):
                return clean(activity.type)

            if activity and getattr(activity, "activity_type", None):
                return clean(activity.activity_type)

            return None

        def event_position(event):
            if hasattr(event, "position"):
                return clean(event.position)

            return None

        return json.dumps({

            "traceId":
                trace.trace_id,

            "context": {

                "legalBasis":
                    clean(trace.context.legal_basis),

                "dataCategory":
                    clean(trace.context.data_category),

                "retentionPeriod":
                    clean(trace.context.retention_period),

                "internationalTransfer":
                    clean(trace.context.international_transfer),

                "hasThirdPartyRecipients":
                    bool(trace.context.has_third_party_recipients),

                "transferSafeguard":
                    clean(trace.context.transfer_safeguard),

                "consentStatus":
                    clean(trace.context.consent_status)
            },

            "events": [

                {
                    "id":
                        getattr(event, "event_id", None),

                    "name":
                        clean(getattr(event, "name", None)),

                    "order":
                        getattr(event, "order", None),

                    "activityType":
                        activity_type(event),

                    "position":
                        event_position(event),

                    "userRightType":
                        clean(getattr(event, "user_right_type", None)),

                    "timestamp":
                        str(event.timestamp)
                        if hasattr(event, "timestamp")
                        else None
                }

                for event in trace.events
            ]

        }, ensure_ascii=True, sort_keys=True)
