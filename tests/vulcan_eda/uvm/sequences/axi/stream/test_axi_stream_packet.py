import pytest

from vulcan_eda.uvm.sequences.axi.stream.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.sequences.axi.stream.axi_stream_packet import AxiStreamPacket

def test_to_beats_single_beat():
    assert AxiStreamPacket(bytes(range(4))).to_beats(4) == [AxiStreamBeat(0x03020100, True)]

def test_to_beats_last_on_final_beat():
    assert AxiStreamPacket(bytes(range(8))).to_beats(4) == [
        AxiStreamBeat(0x03020100, False),
        AxiStreamBeat(0x07060504, True),
    ]

def test_to_beats_rejects_empty():
    with pytest.raises(ValueError):
        AxiStreamPacket(b"").to_beats(4)

def test_to_beats_rejects_partial_beat():
    with pytest.raises(ValueError):
        AxiStreamPacket(bytes(range(5))).to_beats(4)

def test_from_beats_rejects_empty():
    with pytest.raises(ValueError):
        AxiStreamPacket.from_beats([], 4)

@pytest.mark.parametrize("beats", [
    [AxiStreamBeat(0, False)],
    [AxiStreamBeat(0, True), AxiStreamBeat(0, True)],
])
def test_from_beats_rejects_misplaced_last(beats):
    with pytest.raises(ValueError):
        AxiStreamPacket.from_beats(beats, 4)

def test_identity_invariant():
    packet = AxiStreamPacket(bytes(range(64)))
    assert AxiStreamPacket.from_beats(packet.to_beats(8), 8) == packet
