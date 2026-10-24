from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataTransmitterInterface(ReadyValidDataInterface):
    async def put_data(self, data):
        await self._write_edge()
        self._valid_data_interface.write_valid_data(1, self._to_values(data))
        await self._is_consumed()

    async def put_idle(self):
        await self._write_edge()
        self._valid_data_interface.write_idle()

    def _to_values(self, data):
        if self._data_type is None:
            return data
        return data.to_values()
