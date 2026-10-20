import abc

class BaseInterface(abc.ABC):
    @abc.abstractmethod
    async def put(self, sequence_item):
        ...

    @abc.abstractmethod
    async def get(self):
        ...
