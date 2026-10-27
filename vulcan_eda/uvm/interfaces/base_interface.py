import abc

class BaseInterface(abc.ABC):
    async def run(self, driver):
        await self.drive_idle()
        while True:
            await driver.drive(await driver.next())

    @abc.abstractmethod
    async def drive_data(self, data):
        ...

    @abc.abstractmethod
    async def drive_idle(self):
        ...

    @abc.abstractmethod
    async def get_data(self):
        ...
