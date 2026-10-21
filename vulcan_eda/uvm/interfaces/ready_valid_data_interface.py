import cocotb

from vulcan_eda.uvm.interfaces import DataInterface, ValidDataInterface
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequenceItem

class ReadyValidDataInterface:
    def __init__(self, clk, ready, valid, data):
        self._ready_interface = DataInterface(clk, ready)
        self._valid_data_interface = ValidDataInterface(clk, valid, data)

    async def put(self, sequence_item):
        if isisnstance(sequence_item, DataSequence):
            await self.put_ready(sequence_item.data)
        elif isinstance(sequence_item, ValidDataSequence):
            await self.put_valid_data(sequence_item.valid, sequence_item.data)

    async def put_ready(self, ready):
        await self._ready_interface.put_data(ready)

    async def put_valid_data(self, valid, data):
        await self._ready_interface.put_data(valid)
        if valid:
            await self._is_consumed()

    async def get(self):
        return await self._is_consumed()

    async def _is_consumed(self):
        valid_data_interface_task = cocotb.start_soon(self._valid_data_interface.get())
        while not await self._ready_interface.get():
            pass
        return await valid_data_interface_task
