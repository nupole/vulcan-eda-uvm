from vulcan_eda.uvm.generators.hold_generator import HoldGenerator
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.signals.signal import Signal

class DataInterface(BaseInterface):
    def __init__(self, clk, data, idle_generator=None):
        super().__init__(clk)
        self._data = Signal.wrap(data)
        self._idle_iter = iter(HoldGenerator(self._data) if idle_generator is None else idle_generator)

    async def put_data(self, data):
        await self._write_edge()
        self.write_data(data)

    async def put_idle(self):
        await self._write_edge()
        self.write_idle()

    async def get_data(self):
        await self._read_edge()
        return self.read_data()

    def read_data(self):
        return self._data.value

    def write_data(self, data):
        self._data.value = data

    def write_idle(self):
        self._data.value = next(self._idle_iter)
