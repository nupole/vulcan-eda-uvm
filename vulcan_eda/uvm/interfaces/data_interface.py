import cocotb

from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

class DataInterface(BaseInterface):
    def __init__(self, clk, data):
        self._clk = clk
        self._data = data

    async def put(self, sequence_item):
        async def put(self, sequence_item):
            await self.put_data(sequence_item.data)

    async def put_data(self, data):
        await cocotb.triggers.RisingEdge(self._clk)
        self._data.value = data

    async def get(self):
        while True:
            await cocotb.triggers.FallingEdge(self._clk)
            if self._data_pin.value.is_resolvable:
                return self._data.value
