import abc

class BaseSignal(abc.ABC):
    @property
    @abc.abstractmethod
    def value(self):
        ...

    @abc.abstractmethod
    def random_value(self):
        ...
