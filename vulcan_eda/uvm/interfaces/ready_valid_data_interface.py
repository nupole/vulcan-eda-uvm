from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.interfaces.data_interface import DataInterface
from vulcan_eda.uvm.interfaces.valid_data_interface import ValidDataInterface

class ReadyValidDataInterface(BaseInterface):
    def __init__(self, clk, ready, valid, data, data_type=None, idle_generator=None):
        super().__init__(clk)
        self._data_type = data_type
        if data_type is not None:
            data = data_type.signals(**data)
        self._ready_interface = DataInterface(clk, ready, idle_generator)
        self._valid_data_interface = ValidDataInterface(clk, valid, data, idle_generator)

    async def get_data(self):
        return self._from_values(await self._is_consumed())

    def read_ready_valid_data(self):
        ready = self._ready_interface.read_data()
        valid, data = self._valid_data_interface.read_valid_data()
        return ready, valid, data

    async def _is_consumed(self):
        while True:
            await self._read_edge()
            ready, valid, data = self.read_ready_valid_data()
            if ready == 1 and valid == 1:
                return data

    def _from_values(self, values):
        if self._data_type is None:
            return values
        return self._data_type.from_values(values)
