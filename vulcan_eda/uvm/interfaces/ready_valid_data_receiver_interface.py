from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface

class ReadyValidDataReceiverInterface(ReadyValidDataInterface):
    async def drive_data(self, ready):
        self._ready_interface.write_data(ready)

    async def drive_idle(self):
        self._ready_interface.write_idle()
