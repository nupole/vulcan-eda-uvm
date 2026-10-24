from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataTransmitterInterface(ReadyValidDataInterface):
    async def put(self, sequence_item):
        await self.put_valid_data(sequence_item.valid, sequence_item.data)

    async def put_valid_data(self, valid, data):
        await self._write_edge()
        self._valid_data_interface.write_valid_data(valid, None if data is None else self._to_values(data))
        if valid:
            await self._is_consumed()

    def _to_values(self, data):
        if self._data_type is None:
            return data
        return data.to_values()
