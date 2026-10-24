from vulcan_eda.uvm.generators.random_signal_generator import RandomSignalGenerator
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.interfaces.data_interface import DataInterface

class ValidDataInterface(BaseInterface):
    def __init__(self, clk, valid, data, idle_generator=None):
        super().__init__(clk)
        self._valid_interface = DataInterface(clk, valid)
        self._data_interface = DataInterface(clk, data, RandomSignalGenerator(data) if idle_generator is None else idle_generator)

    async def drive_data(self, data):
        self.write_valid_data(1, data)

    async def drive_idle(self):
        self.write_idle()

    async def get_data(self):
        while True:
            await self._read_edge()
            valid, data = self.read_valid_data()
            if valid == 1:
                return data

    def read_valid_data(self):
        return self._valid_interface.read_data(), self._data_interface.read_data()

    def write_valid_data(self, valid, data):
        self._valid_interface.write_data(valid)
        self._data_interface.write_data(data)

    def write_idle(self):
        self._valid_interface.write_data(0)
        self._data_interface.write_idle()
