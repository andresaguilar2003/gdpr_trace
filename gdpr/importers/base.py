from abc import ABC, abstractmethod

class BaseImporter(ABC):

    @abstractmethod
    def load(self, path):
        """
        Devuelve un pm4py EventLog
        """
        pass
