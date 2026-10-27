import cocotb

from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class SynchronousInterface(BaseInterface):
    def __init__(self, clk):
        self._clk = clk

    async def put_data(self, data):
        await self.write_edge()
        await self.drive_data(data)

    async def put_idle(self):
        await self.write_edge()
        await self.drive_idle()

    async def write_edge(self):
        await cocotb.triggers.RisingEdge(self._clk)

    async def read_edge(self):
        await cocotb.triggers.FallingEdge(self._clk)
