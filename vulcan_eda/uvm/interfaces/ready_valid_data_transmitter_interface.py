from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataTransmitterInterface(ReadyValidDataInterface):
    async def drive_data(self, data):
        self._valid_data_interface.write_valid_data(1, self._to_values(data))
        await self._is_consumed()

    async def drive_idle(self):
        self._valid_data_interface.write_idle()

    def _to_values(self, data):
        if self._data_type is None:
            return data
        return data.to_values()
