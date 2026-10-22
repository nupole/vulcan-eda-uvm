from vulcan_eda.uvm.interfaces.base_interface import BaseInterface
from vulcan_eda.uvm.interfaces.ready_valid_data_interface import ReadyValidDataInterface
from vulcan_eda.uvm.sequences.axi.stream.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.sequences.axi.stream.axi_stream_beat_sequence import AxiStreamBeatSequenceItem
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
from vulcan_eda.uvm.signals import Bundle

class AxiStreamInterface(BaseInterface):
    def __init__(self, clk, tready, tvalid, tdata, tlast):
        self._ready_valid_data_interface = ReadyValidDataInterface(clk, tready, tvalid, Bundle(tdata, tlast))

    async def put(self, sequence_item):
        if isinstance(sequence_item, DataSequenceItem):
            await self.put_ready(sequence_item.data)
        elif isinstance(sequence_item, AxiStreamBeatSequenceItem):
            await self.put_beat(sequence_item.valid, sequence_item.beat)

    async def put_ready(self, ready):
        await self._ready_valid_data_interface.put_ready(ready)

    async def put_beat(self, valid, beat):
        await self._ready_valid_data_interface.put_valid_data(valid, (beat.data, beat.last))

    async def get(self):
        data, last = await self._ready_valid_data_interface.get()
        return AxiStreamBeat(int(data), bool(last))
