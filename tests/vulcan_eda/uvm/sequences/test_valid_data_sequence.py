import asyncio
import itertools

import pytest

from vulcan_eda.uvm.generators import ConstantGenerator, IterableGenerator, PatternGenerator, RandomBooleanGenerator
from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem
from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequence

def run_valid_data_sequence(sequencer, data_generator, valid_generator=None):
    valid_data_sequence = ValidDataSequence.create("valid_data_sequence")
    valid_data_sequence.data_generator = data_generator
    if valid_generator is not None:
        valid_data_sequence.valid_generator = valid_generator
    asyncio.run(valid_data_sequence.start(sequencer))
    return [(False, None) if isinstance(item, IdleSequenceItem) else (True, item.data) for item in sequencer.items]

def test_valid_data_sequence_is_always_valid_by_default(recording_sequencer):
    assert run_valid_data_sequence(recording_sequencer, (3, 1)) == [(True, 3), (True, 1)]

def test_valid_data_sequence_follows_its_valid_generator(recording_sequencer):
    assert run_valid_data_sequence(recording_sequencer, (3, 1), PatternGenerator((0, 1))) == [(False, None), (True, 3), (False, None), (True, 1)]

def test_valid_data_sequence_sends_every_value_once_under_random_valid(recording_sequencer):
    items = run_valid_data_sequence(recording_sequencer, range(50), RandomBooleanGenerator(50, seed=1))
    assert [data for valid, data in items if valid] == list(range(50))
    assert {data for valid, data in items if not valid} == {None}
    assert len(items) > 50

def test_valid_data_sequence_sends_nothing_for_empty_data(recording_sequencer):
    assert run_valid_data_sequence(recording_sequencer, ()) == []

def test_valid_data_sequence_restarts_re_iterable_generators(recording_sequencer):
    valid_data_sequence = ValidDataSequence.create("valid_data_sequence")
    valid_data_sequence.data_generator = IterableGenerator((3, 1))
    asyncio.run(valid_data_sequence.start(recording_sequencer))
    asyncio.run(valid_data_sequence.start(recording_sequencer))
    assert [item.data for item in recording_sequencer.items] == [3, 1, 3, 1]

def test_valid_data_sequence_requires_a_data_generator(recording_sequencer):
    with pytest.raises(ValueError, match="data_generator"):
        asyncio.run(ValidDataSequence.create("valid_data_sequence").start(recording_sequencer))

def test_valid_data_sequence_rejects_a_valid_generator_that_runs_out(recording_sequencer):
    with pytest.raises(ValueError, match="valid_generator"):
        run_valid_data_sequence(recording_sequencer, (3, 1, 2), itertools.repeat(True, 2))

@pytest.mark.parametrize("attribute", ["valid_generator", "data_generator"])
def test_valid_data_sequence_rejects_generators_that_are_not_iterable_when_set(attribute):
    with pytest.raises(TypeError):
        setattr(ValidDataSequence.create("valid_data_sequence"), attribute, 5)

def test_valid_data_sequence_generators_can_be_read_back():
    valid_data_sequence = ValidDataSequence.create("valid_data_sequence")
    valid_generator, data_generator = PatternGenerator((1, 0)), (3, 1)
    valid_data_sequence.valid_generator = valid_generator
    valid_data_sequence.data_generator = data_generator
    assert (valid_data_sequence.valid_generator, valid_data_sequence.data_generator) == (valid_generator, data_generator)

def test_valid_data_sequence_defaults_to_always_valid():
    assert ValidDataSequence.create("valid_data_sequence").valid_generator == ConstantGenerator(True)

def test_valid_data_sequence_sends_data_and_idle_items(recording_sequencer):
    run_valid_data_sequence(recording_sequencer, (3,), PatternGenerator((0, 1)))
    assert [type(item) for item in recording_sequencer.items] == [IdleSequenceItem, DataSequenceItem]
