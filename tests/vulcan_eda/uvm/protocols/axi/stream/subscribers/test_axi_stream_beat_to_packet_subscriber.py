import pytest
import pyuvm

from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.data import AxiStreamPacket
from vulcan_eda.uvm.protocols.axi.stream.subscribers import AxiStreamBeatToPacketSubscriber

PACKETS = [AxiStreamPacket(bytes(range(8))), AxiStreamPacket(bytes(range(8, 12)))]

def build(recording_subscriber):
    AxiStreamConfig(num_bytes=4).set(None, "axi_stream_beat_to_packet_subscriber")
    axi_stream_beat_to_packet_subscriber = AxiStreamBeatToPacketSubscriber.create("axi_stream_beat_to_packet_subscriber", None)
    axi_stream_beat_to_packet_subscriber.build_phase()
    axi_stream_beat_to_packet_subscriber.analysis_port.connect(recording_subscriber.analysis_export)
    return axi_stream_beat_to_packet_subscriber

def test_publishes_nothing_before_last(recording_subscriber):
    axi_stream_beat_to_packet_subscriber = build(recording_subscriber)
    axi_stream_beat_to_packet_subscriber.analysis_exports["stream"].write(PACKETS[0].to_beats(4)[0])
    assert recording_subscriber.items == []

def test_publishes_each_packet_at_last(recording_subscriber):
    axi_stream_beat_to_packet_subscriber = build(recording_subscriber)
    for packet in PACKETS:
        for beat in packet.to_beats(4):
            axi_stream_beat_to_packet_subscriber.analysis_exports["stream"].write(beat)
    assert recording_subscriber.items == PACKETS

def test_requires_axi_stream_config():
    axi_stream_beat_to_packet_subscriber = AxiStreamBeatToPacketSubscriber.create("axi_stream_beat_to_packet_subscriber", None)
    with pytest.raises(pyuvm.UVMConfigItemNotFound):
        axi_stream_beat_to_packet_subscriber.build_phase()
