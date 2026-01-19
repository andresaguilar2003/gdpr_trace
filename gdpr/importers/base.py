from abc import ABC, abstractmethod

class BaseImporter(ABC):

    @abstractmethod
    def load(self, path):
        """
        Carga un archivo y devuelve un pm4py EventLog
        """
        pass
