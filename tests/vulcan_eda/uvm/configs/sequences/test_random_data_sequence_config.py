import pytest

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig

def test_defaults():
    assert RandomDataSequenceConfig() == RandomDataSequenceConfig(min_data=0, max_data=255)

def test_accepts_signed_range():
    assert RandomDataSequenceConfig(min_data=-128, max_data=127).min_data == -128

def test_rejects_min_data_greater_than_max_data():
    with pytest.raises(ValueError):
        RandomDataSequenceConfig(min_data=1, max_data=0)
