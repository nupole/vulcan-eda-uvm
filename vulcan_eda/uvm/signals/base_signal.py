import abc

class BaseSignal(abc.ABC):
    @property
    @abc.abstractmethod
    def value(self):
        ...

    @property
    @abc.abstractmethod
    def value_change(self):
        ...

    @abc.abstractmethod
    def random_value(self):
        ...
