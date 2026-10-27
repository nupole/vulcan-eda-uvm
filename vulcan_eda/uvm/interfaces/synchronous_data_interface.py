from vulcan_eda.uvm.interfaces.base_data_interface import BaseDataInterface
from vulcan_eda.uvm.interfaces.synchronous_interface import SynchronousInterface

class SynchronousDataInterface(SynchronousInterface, BaseDataInterface):
    def __init__(self, clk, data, idle_generator=None):
        SynchronousInterface.__init__(self, clk)
        BaseDataInterface.__init__(self, data, idle_generator)

    async def get_data(self):
        await self.read_edge()
        return self.read_data()
