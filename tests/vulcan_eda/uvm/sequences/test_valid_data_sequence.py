import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig
from vulcan_eda.uvm.configs.sequences.transaction_sequence_config import TransactionSequenceConfig
from vulcan_eda.uvm.sequences.valid_data_sequence import IterableValidDataSequence, RandomValidDataSequence

@pytest.mark.parametrize("is_txn", [True, False])
def test_random_valid_data_sequence_uses_min_data(is_txn):
    pyuvm.ConfigDB().set(None, "", "random_data_sequence_config", RandomDataSequenceConfig(min_data=-5, max_data=-5))
    random_valid_data_sequence = RandomValidDataSequence("random_valid_data_sequence")
    random_valid_data_sequence._configure()
    assert random_valid_data_sequence._get_next_sequence_item(is_txn).data == -5

def run_iterable_valid_data_sequence(sequencer, iterable):
    iterable_valid_data_sequence = IterableValidDataSequence.create("iterable_valid_data_sequence")
    iterable_valid_data_sequence.iterable = iterable
    asyncio.run(iterable_valid_data_sequence.start(sequencer))
    return [(item.valid, item.data) for item in sequencer.items]

def test_iterable_valid_data_sequence_sends_each_element_once_then_idles(recording_sequencer):
    assert run_iterable_valid_data_sequence(recording_sequencer, (3, 1, 2)) == [(True, 3), (True, 1), (True, 2), (False, 2)]

def test_iterable_valid_data_sequence_accepts_a_generator(recording_sequencer):
    assert run_iterable_valid_data_sequence(recording_sequencer, (data for data in range(2))) == [(True, 0), (True, 1), (False, 1)]

def test_iterable_valid_data_sequence_ignores_max_num_txn(recording_sequencer):
    pyuvm.ConfigDB().set(recording_sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(max_num_txn=1))
    assert [data for valid, data in run_iterable_valid_data_sequence(recording_sequencer, (3, 1, 2)) if valid] == [3, 1, 2]

def test_iterable_valid_data_sequence_idles_hold_previous_data(recording_sequencer):
    pyuvm.ConfigDB().set(recording_sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
    items = run_iterable_valid_data_sequence(recording_sequencer, (3, 1, 2))
    assert [data for valid, data in items if valid] == [3, 1, 2]
    previous_data = 3
    for valid, data in items:
        if not valid:
            assert data == previous_data
        previous_data = data

def test_iterable_valid_data_sequence_requires_elements(recording_sequencer):
    with pytest.raises(ValueError):
        run_iterable_valid_data_sequence(recording_sequencer, ())
