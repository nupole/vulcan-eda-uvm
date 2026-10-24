import dataclasses

import pytest

from vulcan_eda.uvm.generators import IterableGenerator

def test_yields_each_value_then_stops():
    assert list(IterableGenerator((3, 1, 2))) == [3, 1, 2]

def test_each_iteration_is_independent():
    iterable_generator = IterableGenerator((3, 1, 2))
    first = iter(iterable_generator)
    next(first)
    assert list(iterable_generator) == [3, 1, 2]

def test_one_shot_iterables_become_re_iterable():
    iterable_generator = IterableGenerator(value for value in (3, 1, 2))
    assert list(iterable_generator) == list(iterable_generator) == [3, 1, 2]

def test_may_be_empty():
    assert list(IterableGenerator(())) == []

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        IterableGenerator((3, 1, 2)).values = ()

def test_repr_shows_its_values():
    assert repr(IterableGenerator([3, 1, 2])) == "IterableGenerator(values=(3, 1, 2))"
