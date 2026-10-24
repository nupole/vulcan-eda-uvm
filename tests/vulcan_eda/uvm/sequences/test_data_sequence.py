import asyncio
import itertools

import pytest
import pyuvm

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig
from vulcan_eda.uvm.configs.sequences.transaction_sequence_config import TransactionSequenceConfig
from vulcan_eda.uvm.generators import IterableGenerator, RandomBooleanGenerator
from vulcan_eda.uvm.sequences.data_sequence import DataSequence, IterableDataSequence, RandomDataSequence

def test_random_data_sequence_uses_min_data():
    pyuvm.ConfigDB().set(None, "", "random_data_sequence_config", RandomDataSequenceConfig(min_data=-5, max_data=-5))
    random_data_sequence = RandomDataSequence("random_data_sequence")
    random_data_sequence._configure()
    assert random_data_sequence._get_next_sequence_item(True).data == -5

def run_iterable_data_sequence(sequencer, iterable):
    iterable_data_sequence = IterableDataSequence.create("iterable_data_sequence")
    iterable_data_sequence.iterable = iterable
    asyncio.run(iterable_data_sequence.start(sequencer))
    return [item.data for item in sequencer.items]

def test_iterable_data_sequence_sends_each_element_once(recording_sequencer):
    assert run_iterable_data_sequence(recording_sequencer, (3, 1, 2)) == [3, 1, 2]

def test_iterable_data_sequence_sends_single_element(recording_sequencer):
    assert run_iterable_data_sequence(recording_sequencer, (1,)) == [1]

def test_iterable_data_sequence_accepts_a_generator(recording_sequencer):
    assert run_iterable_data_sequence(recording_sequencer, (data for data in range(3))) == [0, 1, 2]

def test_iterable_data_sequence_ignores_max_num_txn(recording_sequencer):
    pyuvm.ConfigDB().set(recording_sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(max_num_txn=1))
    assert run_iterable_data_sequence(recording_sequencer, (3, 1, 2)) == [3, 1, 2]

def test_iterable_data_sequence_requires_txn_pct_100(recording_sequencer):
    pyuvm.ConfigDB().set(recording_sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
    with pytest.raises(ValueError):
        run_iterable_data_sequence(recording_sequencer, (3, 1, 2))

def test_iterable_data_sequence_requires_elements(recording_sequencer):
    with pytest.raises(ValueError):
        run_iterable_data_sequence(recording_sequencer, ())

def run_data_sequence(sequencer, data_generator):
    data_sequence = DataSequence.create("data_sequence")
    data_sequence.data_generator = data_generator
    asyncio.run(data_sequence.start(sequencer))
    return data_sequence

def test_data_sequence_sends_each_value_in_order(recording_sequencer):
    run_data_sequence(recording_sequencer, (1, 1, 1, 0))
    assert [item.data for item in recording_sequencer.items] == [1, 1, 1, 0]

def test_data_sequence_sends_nothing_for_empty_data(recording_sequencer):
    run_data_sequence(recording_sequencer, ())
    assert recording_sequencer.items == []

def test_data_sequence_accepts_generators(recording_sequencer):
    run_data_sequence(recording_sequencer, itertools.islice(RandomBooleanGenerator(50), 20))
    assert {item.data for item in recording_sequencer.items} == {False, True}

def test_data_sequence_restarts_a_re_iterable_data_generator(recording_sequencer):
    data_sequence = run_data_sequence(recording_sequencer, IterableGenerator((1, 0)))
    asyncio.run(data_sequence.start(recording_sequencer))
    assert [item.data for item in recording_sequencer.items] == [1, 0, 1, 0]

def test_data_sequence_requires_a_data_generator(recording_sequencer):
    with pytest.raises(ValueError):
        asyncio.run(DataSequence.create("data_sequence").start(recording_sequencer))
