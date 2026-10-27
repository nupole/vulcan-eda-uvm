import cocotb

from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class SynchronousInterface(BaseInterface):
    def __init__(self, clk):
        self._clk = clk

    async def run(self, driver):
        while True:
            await self.write_edge()
            sequence_item = await driver.try_next()
            if sequence_item is None:
                await self.drive_idle()
            else:
                await driver.drive(sequence_item)

    async def write_edge(self):
        await cocotb.triggers.RisingEdge(self._clk)

    async def read_edge(self):
        await cocotb.triggers.FallingEdge(self._clk)
