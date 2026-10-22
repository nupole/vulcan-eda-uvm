from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataTransmitterInterface(ReadyValidDataInterface):
    async def put(self, sequence_item):
        await self.put_valid_data(sequence_item.valid, sequence_item.data)
