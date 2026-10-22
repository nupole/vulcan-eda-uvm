import cocotb

from vulcan_eda.uvm.interfaces import DataInterface
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class ValidDataInterface(BaseInterface):
    def __init__(self, clk, valid, data):
        super().__init__(clk)
        self._valid_interface = DataInterface(clk, valid)
        self._data_interface = DataInterface(clk, data)

    async def put(self, sequence_item):
        await self.put_valid_data(sequence_item.valid, sequence_item.data)

    async def put_valid_data(self, valid, data):
        valid_interface_task = cocotb.start_soon(self._valid_interface.put_data(valid))
        data_interface_task = cocotb.start_soon(self._data_interface.put_data(data))
        await cocotb.triggers.Combine(valid_interface_task, data_interface_task)

    async def get(self):
        while True:
            valid, data = await self.get_valid_data()
            if valid == 1:
                return data

    async def get_valid_data(self):
        valid_interface_task = cocotb.start_soon(self._valid_interface.get())
        data_interface_task = cocotb.start_soon(self._data_interface.get())
        await cocotb.triggers.Combine(valid_interface_task, data_interface_task)
        return valid_interface_task.result(), data_interface_task.result()
