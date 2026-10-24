import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import WalkingOneHotGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_walks_a_single_one_through_each_bit_then_repeats():
    assert take(WalkingOneHotGenerator(4), 6) == [0b0001, 0b0010, 0b0100, 0b1000, 0b0001, 0b0010]

def test_width_one_stays_at_one():
    assert take(WalkingOneHotGenerator(1), 3) == [1, 1, 1]

def test_each_iteration_is_independent():
    walking_one_hot_generator = WalkingOneHotGenerator(4)
    first = iter(walking_one_hot_generator)
    next(first)
    assert take(walking_one_hot_generator, 2) == [1, 2]

@pytest.mark.parametrize("width", [-1, 0])
def test_rejects_width_not_positive(width):
    with pytest.raises(ValueError):
        WalkingOneHotGenerator(width)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        WalkingOneHotGenerator(4).width = 8

def test_repr_shows_its_width():
    assert repr(WalkingOneHotGenerator(4)) == "WalkingOneHotGenerator(width=4)"
