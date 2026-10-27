from vulcan_eda.uvm.interfaces.base_data_interface import BaseDataInterface

class AsynchronousDataInterface(BaseDataInterface):
    async def get_data(self):
        await self._data.value_change
        return self.read_data()
