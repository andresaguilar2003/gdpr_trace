from abc import ABC, abstractmethod


class BaseMutation(ABC):

    name = "base_mutation"
    category = "generic"

    @abstractmethod
    def apply(self, trace):
        pass