from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataReceiverInterface(ReadyValidDataInterface):
    async def put_data(self, ready):
        await self._write_edge()
        self._ready_interface.write_data(ready)

    async def put_idle(self):
        await self._write_edge()
        self._ready_interface.write_idle()
