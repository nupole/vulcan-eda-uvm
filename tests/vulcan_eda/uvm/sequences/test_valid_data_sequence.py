import pytest
import pyuvm

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig
from vulcan_eda.uvm.sequences.valid_data_sequence import RandomValidDataSequence

@pytest.mark.parametrize("is_txn", [True, False])
def test_random_valid_data_sequence_uses_min_data(is_txn):
    pyuvm.ConfigDB().set(None, "", "random_data_sequence_config", RandomDataSequenceConfig(min_data=-5, max_data=-5))
    random_valid_data_sequence = RandomValidDataSequence("random_valid_data_sequence")
    random_valid_data_sequence._configure()
    assert random_valid_data_sequence._get_next_sequence_item(is_txn).data == -5
