from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataReceiverInterface(ReadyValidDataInterface):
    async def put(self, sequence_item):
        await self.put_ready(sequence_item.data)

    async def put_ready(self, ready):
        await self._ready_interface.put_data(ready)
