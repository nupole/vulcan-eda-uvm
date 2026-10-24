import abc

import cocotb

class BaseInterface(abc.ABC):
    def __init__(self, clk):
        self._clk = clk

    @abc.abstractmethod
    async def put_data(self, data):
        ...

    @abc.abstractmethod
    async def put_idle(self):
        ...

    @abc.abstractmethod
    async def get_data(self):
        ...

    async def _write_edge(self):
        await cocotb.triggers.RisingEdge(self._clk)

    async def _read_edge(self):
        await cocotb.triggers.FallingEdge(self._clk)
