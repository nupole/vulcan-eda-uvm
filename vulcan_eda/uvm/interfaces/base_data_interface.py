from vulcan_eda.uvm.generators.hold_generator import HoldGenerator
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.signals.signal import Signal

class BaseDataInterface(BaseInterface):
    def __init__(self, data, idle_generator=None):
        self._data = Signal.wrap(data)
        self._idle_iter = iter(HoldGenerator(self._data) if idle_generator is None else idle_generator)

    async def drive_data(self, data):
        self.write_data(data)

    async def drive_idle(self):
        self.write_idle()

    def read_data(self):
        return self._data.value

    def write_data(self, data):
        self._data.value = data

    def write_idle(self):
        self._data.value = next(self._idle_iter)
