import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.generators import PatternGenerator
from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketToBeatSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.data import AxiStreamPacket
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_packet_to_beat_sequence import AxiStreamPacketToBeatSequence
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequence

class CountingValidDataSequence(ValidDataSequence):
    starts = 0

    async def body(self):
        CountingValidDataSequence.starts += 1
        await super().body()

PACKETS = [AxiStreamPacket(bytes(range(8))), AxiStreamPacket(bytes(range(8, 12)))]

def run(sequencer, upper_sequencer, packets):
    pyuvm.ConfigDB().set(upper_sequencer, "", "axi_stream_config", AxiStreamConfig(num_bytes=4))
    upper_sequencer.items.extend(DataSequenceItem("packet", packet) for packet in packets)
    axi_stream_packet_to_beat_sequence = AxiStreamPacketToBeatSequence.create("axi_stream_packet_to_beat_sequence")
    axi_stream_packet_to_beat_sequence.upper_sequencer = upper_sequencer
    axi_stream_packet_to_beat_sequence.lower_sequencers = {"stream": sequencer}
    with pytest.raises(upper_sequencer.Drained):
        asyncio.run(axi_stream_packet_to_beat_sequence.start())

def test_sends_each_packet_as_beats(recording_sequencer, upper_sequencer):
    run(recording_sequencer, upper_sequencer, PACKETS)
    valid_beats = [item.data for item in recording_sequencer.items if not isinstance(item, IdleSequenceItem)]
    assert valid_beats == PACKETS[0].to_beats(4) + PACKETS[1].to_beats(4)

def test_finishes_each_packet(recording_sequencer, upper_sequencer):
    run(recording_sequencer, upper_sequencer, PACKETS)
    assert [item.data for item in upper_sequencer.done_items] == PACKETS

def test_valid_data_sequence_can_be_overridden(recording_sequencer, upper_sequencer):
    pyuvm.uvm_factory().set_type_override_by_type(ValidDataSequence, CountingValidDataSequence)
    CountingValidDataSequence.starts = 0
    run(recording_sequencer, upper_sequencer, PACKETS)
    assert CountingValidDataSequence.starts == len(PACKETS)

def test_uses_the_configured_valid_generator(recording_sequencer, upper_sequencer):
    pyuvm.ConfigDB().set(upper_sequencer, "", "axi_stream_packet_to_beat_sequence_config", AxiStreamPacketToBeatSequenceConfig(PatternGenerator((0, 1))))
    run(recording_sequencer, upper_sequencer, PACKETS[1:])
    assert [type(item) for item in recording_sequencer.items] == [IdleSequenceItem, DataSequenceItem]

def test_sends_packets_back_to_back_by_default(recording_sequencer, upper_sequencer):
    run(recording_sequencer, upper_sequencer, PACKETS)
    assert [type(item) for item in recording_sequencer.items] == [DataSequenceItem, DataSequenceItem, DataSequenceItem]
