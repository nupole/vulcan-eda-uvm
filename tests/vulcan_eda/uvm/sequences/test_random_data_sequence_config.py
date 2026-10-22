import pytest

from vulcan_eda.uvm.sequences.random_data_sequence_config import RandomDataSequenceConfig

def test_defaults():
    assert RandomDataSequenceConfig() == RandomDataSequenceConfig(max_data=255)

def test_rejects_negative_max_data():
    with pytest.raises(ValueError):
        RandomDataSequenceConfig(max_data=-1)
