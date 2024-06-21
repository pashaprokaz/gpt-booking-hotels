from abc import ABC, abstractmethod


class BaseDataLoader(ABC):
    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def load_with_filters(self, **kwargs):
        pass
