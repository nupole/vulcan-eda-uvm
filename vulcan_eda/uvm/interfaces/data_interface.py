from vulcan_eda.uvm.generators.hold_generator import HoldGenerator
from vulcan_eda.uvm.interfaces.synchronous_interface import SynchronousInterface
from vulcan_eda.uvm.signals.signal import Signal

class DataInterface(SynchronousInterface):
    def __init__(self, clk, data, idle_generator=None):
        super().__init__(clk)
        self._data = Signal.wrap(data)
        self._idle_iter = iter(HoldGenerator(self._data) if idle_generator is None else idle_generator)

    async def drive_data(self, data):
        self.write_data(data)

    async def drive_idle(self):
        self.write_idle()

    async def get_data(self):
        await self.read_edge()
        return self.read_data()

    def read_data(self):
        return self._data.value

    def write_data(self, data):
        self._data.value = data

    def write_idle(self):
        self._data.value = next(self._idle_iter)
