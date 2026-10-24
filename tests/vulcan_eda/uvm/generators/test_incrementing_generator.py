import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import IncrementingGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_counts_up_from_zero_by_default():
    assert take(IncrementingGenerator(), 4) == [0, 1, 2, 3]

def test_uses_start_and_step():
    assert take(IncrementingGenerator(start=10, step=5), 3) == [10, 15, 20]

def test_counts_down_with_a_negative_step():
    assert take(IncrementingGenerator(start=2, step=-1), 4) == [2, 1, 0, -1]

def test_wraps_at_width():
    assert take(IncrementingGenerator(start=6, width=3), 4) == [6, 7, 0, 1]

def test_wraps_down_at_width():
    assert take(IncrementingGenerator(start=1, step=-1, width=3), 3) == [1, 0, 7]

def test_each_iteration_is_independent():
    incrementing_generator = IncrementingGenerator()
    first = iter(incrementing_generator)
    next(first)
    assert take(incrementing_generator, 2) == [0, 1]

@pytest.mark.parametrize("width", [-1, 0])
def test_rejects_width_not_positive(width):
    with pytest.raises(ValueError):
        IncrementingGenerator(width=width)

@pytest.mark.parametrize("start", [-1, 8])
def test_rejects_start_outside_width(start):
    with pytest.raises(ValueError):
        IncrementingGenerator(start=start, width=3)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        IncrementingGenerator().step = 2

def test_repr_shows_its_fields():
    assert repr(IncrementingGenerator(start=1, step=2, width=8)) == "IncrementingGenerator(start=1, step=2, width=8)"
