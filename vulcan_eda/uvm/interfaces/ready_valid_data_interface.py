import cocotb

from vulcan_eda.uvm.interfaces import DataInterface, ValidDataInterface
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequenceItem

class ReadyValidDataInterface:
    def __init__(self, clk, ready, valid, data):
        self._ready_interface = DataInterface(clk, ready)
        self._valid_data_interface = ValidDataInterface(clk, valid, data)

    async def put(self, sequence_item):
        if isinstance(sequence_item, DataSequenceItem):
            await self.put_ready(sequence_item.data)
        elif isinstance(sequence_item, ValidDataSequenceItem):
            await self.put_valid_data(sequence_item.valid, sequence_item.data)

    async def put_ready(self, ready):
        await self._ready_interface.put_data(ready)

    async def put_valid_data(self, valid, data):
        await self._valid_data_interface.put_valid_data(valid, data)
        if valid:
            await self._is_consumed()

    async def get(self):
        return await self._is_consumed()

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
            if ready and valid:
                return data
