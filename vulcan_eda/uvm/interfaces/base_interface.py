import abc

class BaseInterface(abc.ABC):
    @abc.abstractmethod
    async def drive_data(self, data):
        ...

    @abc.abstractmethod
    async def drive_idle(self):
        ...

    @abc.abstractmethod
    async def get_data(self):
        ...
