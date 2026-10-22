from vulcan_eda.uvm.interfaces import DataInterface, ValidDataInterface
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class ReadyValidDataInterface(BaseInterface):
    def __init__(self, clk, ready, valid, data):
        super().__init__(clk)
        self._ready_interface = DataInterface(clk, ready)
        self._valid_data_interface = ValidDataInterface(clk, valid, data)

    async def get(self):
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
        return values
