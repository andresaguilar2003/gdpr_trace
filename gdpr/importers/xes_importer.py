from pm4py.objects.log.importer.xes import importer as xes_importer
from gdpr.importers.base import BaseImporter

class XESImporter(BaseImporter):

    def load(self, path):
        return xes_importer.apply(path)
