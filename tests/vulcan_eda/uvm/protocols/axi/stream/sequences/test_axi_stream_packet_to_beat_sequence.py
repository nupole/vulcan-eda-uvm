import asyncio
import collections

import pytest
import pyuvm

from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.data import AxiStreamPacket
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_beat_sequence import AxiStreamBeatSequence
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_packet_to_beat_sequence import AxiStreamPacketToBeatSequence
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem

class Drained(Exception):
    pass

class UpperSequencer:
    def __init__(self, items):
        self._items = collections.deque(items)
        self.seq_item_export = self
        self.done_items = []

    async def get_next_item(self):
        if not self._items:
            raise Drained()
        self._current_item = self._items.popleft()
        return self._current_item

    def item_done(self):
        self.done_items.append(self._current_item)

class RecordingSequencer(pyuvm.uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = []

    async def start_item(self, item):
        pass

    async def finish_item(self, item):
        self.items.append(item)

class CountingBeatSequence(AxiStreamBeatSequence):
    starts = 0

    async def body(self):
        CountingBeatSequence.starts += 1
        await super().body()

@pytest.fixture
def factory():
    yield pyuvm.uvm_factory()
    pyuvm.uvm_factory().clear_overrides()

PACKETS = [AxiStreamPacket(bytes(range(8))), AxiStreamPacket(bytes(range(8, 12)))]

def run(packets):
    sequencer = RecordingSequencer("sequencer", None)
    pyuvm.ConfigDB().set(sequencer, "", "axi_stream_config", AxiStreamConfig(num_bytes=4))
    upper_sequencer = UpperSequencer([DataSequenceItem("packet", packet) for packet in packets])
    axi_stream_packet_to_beat_sequence = AxiStreamPacketToBeatSequence.create("axi_stream_packet_to_beat_sequence")
    axi_stream_packet_to_beat_sequence.upper_sequencer = upper_sequencer
    with pytest.raises(Drained):
        asyncio.run(axi_stream_packet_to_beat_sequence.start(sequencer))
    return sequencer, upper_sequencer

def test_sends_each_packet_as_beats():
    sequencer, _ = run(PACKETS)
    valid_beats = [item.data for item in sequencer.items if item.valid]
    assert valid_beats == PACKETS[0].to_beats(4) + PACKETS[1].to_beats(4)

def test_finishes_each_packet():
    _, upper_sequencer = run(PACKETS)
    assert [item.data for item in upper_sequencer.done_items] == PACKETS

def test_beat_sequence_can_be_overridden(factory):
    factory.set_type_override_by_type(AxiStreamBeatSequence, CountingBeatSequence)
    CountingBeatSequence.starts = 0
    run(PACKETS)
    assert CountingBeatSequence.starts == len(PACKETS)
