from gdpr.importers.xes_importer import XESImporter
from gdpr.importers.csv_importer import CSVImporter

def load_event_log(path):
    if path.endswith(".xes"):
        return XESImporter().load(path)
    elif path.endswith(".csv"):
        return CSVImporter().load(path)
    else:
        raise ValueError("Formato no soportado")
