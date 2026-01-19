import json
from datetime import datetime
from pm4py.objects.log.obj import EventLog, Trace, Event
from gdpr.importers.base import BaseImporter

class JSONImporter(BaseImporter):

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log = EventLog()

        for case in data:
            trace = Trace()
            trace.attributes["concept:name"] = case["case_id"]

            for e in case["events"]:
                event = Event()
                event["concept:name"] = e["activity"]
                event["time:timestamp"] = datetime.fromisoformat(e["timestamp"])
                event["gdpr:access"] = e.get("gdpr_access", False)

                trace.append(event)

            log.append(trace)

        return log
