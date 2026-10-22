import cocotb

from vulcan_eda.uvm.interfaces import DataInterface, ValidDataInterface
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class ReadyValidDataInterface(BaseInterface):
    def __init__(self, clk, ready, valid, data):
        self._ready_interface = DataInterface(clk, ready)
        self._valid_data_interface = ValidDataInterface(clk, valid, data)

    async def get(self):
        return self._from_values(await self._is_consumed())

    async def get_ready_valid_data(self):
        ready_interface_task = cocotb.start_soon(self._ready_interface.get())
        valid_data_interface_task = cocotb.start_soon(self._valid_data_interface.get_valid_data())
        await cocotb.triggers.Combine(ready_interface_task, valid_data_interface_task)
        ready = ready_interface_task.result()
        valid, data = valid_data_interface_task.result()
        return ready, valid, data

    async def _is_consumed(self):
        while True:
            ready, valid, data = await self.get_ready_valid_data()
            if ready == 1 and valid == 1:
                return data

    def _from_values(self, values):
        return values
