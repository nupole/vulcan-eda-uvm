from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.interfaces.data_interface import DataInterface

class ValidDataInterface(BaseInterface):
    def __init__(self, clk, valid, data):
        super().__init__(clk)
        self._valid_interface = DataInterface(clk, valid)
        self._data_interface = DataInterface(clk, data)

    async def put(self, sequence_item):
        await self.put_valid_data(sequence_item.valid, sequence_item.data)

    async def put_valid_data(self, valid, data):
        await self._write_edge()
        self.write_valid_data(valid, data)

    async def get(self):
        while True:
            await self._read_edge()
            valid, data = self.read_valid_data()
            if valid == 1:
                return data

    def read_valid_data(self):
        return self._valid_interface.read_data(), self._data_interface.read_data()

    def write_valid_data(self, valid, data):
        self._valid_interface.write_data(valid)
        if data is None:
            self._data_interface.write_random_data()
        else:
            self._data_interface.write_data(data)
