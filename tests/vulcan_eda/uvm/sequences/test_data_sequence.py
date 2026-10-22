import pytest
import pyuvm

from vulcan_eda.uvm.sequences.data_sequence import RandomDataSequence
from vulcan_eda.uvm.sequences.random_data_sequence_config import RandomDataSequenceConfig

@pytest.fixture(autouse=True)
def clear_singletons():
    yield
    pyuvm.uvm_root.clear_singletons()

def test_random_data_sequence_uses_min_data():
    pyuvm.ConfigDB().set(None, "", "random_data_sequence_config", RandomDataSequenceConfig(min_data=-5, max_data=-5))
    random_data_sequence = RandomDataSequence("random_data_sequence")
    random_data_sequence._configure()
    assert random_data_sequence._get_next_sequence_item(True).data == -5
