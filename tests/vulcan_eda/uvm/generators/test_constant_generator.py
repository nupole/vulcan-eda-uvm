import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import ConstantGenerator

def test_yields_its_value_forever():
    assert list(itertools.islice(ConstantGenerator(5), 4)) == [5, 5, 5, 5]

def test_each_iteration_is_independent():
    constant_generator = ConstantGenerator(5)
    first = iter(constant_generator)
    next(first)
    assert next(iter(constant_generator)) == 5

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        ConstantGenerator(5).value = 6

def test_repr_shows_its_value():
    assert repr(ConstantGenerator(5)) == "ConstantGenerator(value=5)"
