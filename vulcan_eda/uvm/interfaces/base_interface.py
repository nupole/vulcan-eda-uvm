import abc

import cocotb

class BaseInterface(abc.ABC):
    def __init__(self, clk):
        self._clk = clk

    async def put_data(self, data):
        await self._write_edge()
        await self.drive_data(data)

    async def put_idle(self):
        await self._write_edge()
        await self.drive_idle()

    async def write_edge(self):
        await self._write_edge()

    @abc.abstractmethod
    async def drive_data(self, data):
        ...

    @abc.abstractmethod
    async def drive_idle(self):
        ...

    @abc.abstractmethod
    async def get_data(self):
        ...

    async def _write_edge(self):
        await cocotb.triggers.RisingEdge(self._clk)

    async def _read_edge(self):
        await cocotb.triggers.FallingEdge(self._clk)
