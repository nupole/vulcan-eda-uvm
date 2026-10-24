import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import HoldGenerator
from vulcan_eda.uvm.signals import Bundle, Constant, Inverted

class Handle:
    def __init__(self, width, value=0):
        self.width = width
        self.value = value

    def __len__(self):
        return self.width

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_yields_the_current_value():
    assert take(HoldGenerator(Handle(8, value=5)), 3) == [5, 5, 5]

def test_follows_the_signal_as_it_changes():
    handle = Handle(8, value=5)
    values = iter(HoldGenerator(handle))
    first = next(values)
    handle.value = 7
    assert (first, next(values)) == (5, 7)

def test_writing_its_value_back_holds_the_signal():
    handle = Handle(4, value=0b0110)
    inverted = Inverted(handle)
    inverted.value = next(iter(HoldGenerator(inverted)))
    assert handle.value == 0b0110

def test_holds_bundles_and_constants():
    assert next(iter(HoldGenerator(Bundle(Handle(8, value=5), Constant(1))))) == (5, 1)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        HoldGenerator(Handle(8)).signal = Handle(8)
