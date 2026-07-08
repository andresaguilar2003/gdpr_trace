import json

class TraceJsonLDSerializer:

    @staticmethod
    def serialize(trace):

        data = {
            "@type": "Trace",
            "traceId": trace.trace_id,
            "events": []
        }

        for event in trace.events:

            data["events"].append({
                "name": event.name,
                "order": event.order,
                "position": (
                    str(event.position)
                    if hasattr(event, "position")
                    else None
                )
            })

        return json.dumps(
            data,
            indent=2
        )