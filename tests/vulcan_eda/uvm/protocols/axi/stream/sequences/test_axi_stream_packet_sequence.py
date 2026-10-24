import asyncio

import pytest

from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.data import AxiStreamPacket
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_packet_sequence import AxiStreamPacketSequence, RandomAxiStreamPacketSequence

@pytest.fixture
def sequencer(recording_sequencer):
    AxiStreamConfig(num_bytes=4).set(recording_sequencer)
    return recording_sequencer

def run(sequencer):
    random_axi_stream_packet_sequence = RandomAxiStreamPacketSequence.create("random_axi_stream_packet_sequence")
    asyncio.run(random_axi_stream_packet_sequence.start(sequencer))
    return [item.data for item in sequencer.items]

def test_sends_default_number_of_packets(sequencer):
    assert len(run(sequencer)) == AxiStreamPacketSequenceConfig().num_packets

def test_sends_configured_number_of_packets(sequencer):
    AxiStreamPacketSequenceConfig(num_packets=3).set(sequencer)
    assert len(run(sequencer)) == 3

def test_sends_packets(sequencer):
    assert all(isinstance(packet, AxiStreamPacket) for packet in run(sequencer))

def test_packets_are_whole_beats_in_range(sequencer):
    AxiStreamPacketSequenceConfig(min_num_beats=2, max_num_beats=3).set(sequencer)
    assert {len(packet.data) for packet in run(sequencer)} <= {8, 12}

def test_get_next_packet_must_be_overridden():
    with pytest.raises(NotImplementedError):
        AxiStreamPacketSequence.create("axi_stream_packet_sequence")._get_next_packet()
