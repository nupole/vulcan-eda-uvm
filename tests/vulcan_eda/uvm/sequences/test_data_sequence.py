import asyncio
import itertools

import pytest

from vulcan_eda.uvm.generators import IterableGenerator, RandomBooleanGenerator
from vulcan_eda.uvm.sequences.data_sequence import DataSequence

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

def test_data_sequence_rejects_a_data_generator_that_is_not_iterable_when_set():
    with pytest.raises(TypeError):
        DataSequence.create("data_sequence").data_generator = 5

def test_data_sequence_data_generator_can_be_read_back():
    data_sequence = DataSequence.create("data_sequence")
    data_generator = IterableGenerator((1, 0))
    data_sequence.data_generator = data_generator
    assert data_sequence.data_generator == data_generator
