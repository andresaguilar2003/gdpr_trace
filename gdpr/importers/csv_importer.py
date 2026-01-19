import pandas as pd
from datetime import datetime
from pm4py.objects.log.obj import EventLog, Trace, Event
from gdpr.importers.base import BaseImporter

class CSVImporter(BaseImporter):

    def load(self, path):
        df = pd.read_csv(path)

        log = EventLog()

        for case_id, group in df.groupby("case_id"):
            trace = Trace()
            trace.attributes["concept:name"] = str(case_id)

            for _, row in group.iterrows():
                event = Event()
                event["concept:name"] = row["activity"]
                event["time:timestamp"] = datetime.fromisoformat(row["timestamp"])

                # Campo GDPR opcional
                if "gdpr_access" in row:
                    event["gdpr:access"] = bool(row["gdpr_access"])

                trace.append(event)

            log.append(trace)

        return log
