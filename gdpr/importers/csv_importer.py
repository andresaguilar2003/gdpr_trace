import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from gdpr.importers.base import BaseImporter

class CSVImporter(BaseImporter):

    def load(self, path):
        df = pd.read_csv(path)

        # EXPECTATIVAS MÍNIMAS:
        # case_id, activity, timestamp

        df = df.rename(columns={
            "case_id": "case:concept:name",
            "activity": "concept:name",
            "timestamp": "time:timestamp"
        })

        event_log = log_converter.apply(df)
        return event_log
