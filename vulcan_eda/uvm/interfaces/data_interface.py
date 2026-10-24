from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.signals.signal import Signal

class DataInterface(BaseInterface):
    def __init__(self, clk, data):
        super().__init__(clk)
        self._data = Signal.wrap(data)

    async def put(self, sequence_item):
        await self.put_data(sequence_item.data)

    async def put_data(self, data):
        await self._write_edge()
        self.write_data(data)

    async def get(self):
        await self._read_edge()
        return self.read_data()

    def read_data(self):
        return self._data.value

    def write_data(self, data):
        self._data.value = data

    def write_random_data(self):
        self._data.value = self._data.random_value()
