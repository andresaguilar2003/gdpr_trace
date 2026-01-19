from gdpr.importers.xes_importer import XESImporter
from gdpr.importers.csv_importer import CSVImporter
from gdpr.importers.json_importer import JSONImporter


def load_event_log(path):
    path = path.lower()

    if path.endswith(".xes") or path.endswith(".xes.gz"):
        return XESImporter().load(path)

    elif path.endswith(".csv"):
        return CSVImporter().load(path)

    elif path.endswith(".json"):
        return JSONImporter().load(path)

    else:
        raise ValueError(f"Formato no soportado: {path}")
