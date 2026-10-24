import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import RandomSignalGenerator
from vulcan_eda.uvm.signals import Bundle, Constant

class Handle:
    def __init__(self, width, value=0):
        self.width = width
        self.value = value

    def __len__(self):
        return self.width

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_yields_random_values_of_the_signal_width():
    assert set(take(RandomSignalGenerator(Handle(2)), 200)) == {0, 1, 2, 3}

def test_keeps_constants_in_bundles():
    values = take(RandomSignalGenerator(Bundle(Handle(8), Constant(1))), 50)
    assert {constant for _, constant in values} == {1} and len({data for data, _ in values}) > 1

def test_values_can_be_driven_back_onto_the_signal():
    bundle = Bundle(Handle(8), Constant(1))
    bundle.value = next(iter(RandomSignalGenerator(bundle)))

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        RandomSignalGenerator(Handle(8)).signal = Handle(8)
