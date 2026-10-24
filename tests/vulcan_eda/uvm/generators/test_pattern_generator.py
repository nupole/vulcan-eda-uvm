import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import PatternGenerator

def test_repeats_its_values_forever():
    assert list(itertools.islice(PatternGenerator((1, 1, 0)), 7)) == [1, 1, 0, 1, 1, 0, 1]

def test_each_iteration_is_independent():
    pattern_generator = PatternGenerator((1, 1, 0))
    first = iter(pattern_generator)
    next(first)
    assert list(itertools.islice(pattern_generator, 3)) == [1, 1, 0]

def test_one_shot_iterables_become_re_iterable():
    pattern_generator = PatternGenerator(value for value in (1, 0))
    assert list(itertools.islice(pattern_generator, 2)) == list(itertools.islice(pattern_generator, 2)) == [1, 0]

def test_rejects_empty_values():
    with pytest.raises(ValueError):
        PatternGenerator(())

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        PatternGenerator((1, 0)).values = (0,)

def test_repr_shows_its_values():
    assert repr(PatternGenerator([1, 1, 0])) == "PatternGenerator(values=(1, 1, 0))"
