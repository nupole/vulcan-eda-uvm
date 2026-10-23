import pytest

from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketSequenceConfig

def test_defaults():
    assert AxiStreamPacketSequenceConfig() == AxiStreamPacketSequenceConfig(num_packets=10, min_num_beats=1, max_num_beats=16)

@pytest.mark.parametrize("num_packets", [-1, 0])
def test_rejects_num_packets_not_positive(num_packets):
    with pytest.raises(ValueError):
        AxiStreamPacketSequenceConfig(num_packets=num_packets)

@pytest.mark.parametrize("min_num_beats", [-1, 0])
def test_rejects_min_num_beats_not_positive(min_num_beats):
    with pytest.raises(ValueError):
        AxiStreamPacketSequenceConfig(min_num_beats=min_num_beats)

def test_rejects_min_num_beats_greater_than_max_num_beats():
    with pytest.raises(ValueError):
        AxiStreamPacketSequenceConfig(min_num_beats=2, max_num_beats=1)
