import random
import types

import cocotb.types
import pytest

from vulcan_eda.uvm.signals.base_signal import BaseSignal
from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

def signal(value):
    return types.SimpleNamespace(value=cocotb.types.LogicArray(value))

def test_value_reads_each_signal():
    assert Bundle(signal("01"), signal("1")).value == (cocotb.types.LogicArray("01"), cocotb.types.LogicArray("1"))

def test_value_drives_each_signal():
    data, last = signal("00"), signal("0")
    Bundle(data, last).value = (cocotb.types.LogicArray("10"), cocotb.types.LogicArray("1"))
    assert (data.value, last.value) == (cocotb.types.LogicArray("10"), cocotb.types.LogicArray("1"))

def test_value_rejects_wrong_length():
    with pytest.raises(ValueError):
        Bundle(signal("00"), signal("0")).value = (cocotb.types.LogicArray("10"),)

def test_nested_bundle():
    bundle = Bundle(Bundle(signal("01"), signal("1")), signal("0"))
    assert bundle.value == ((cocotb.types.LogicArray("01"), cocotb.types.LogicArray("1")), cocotb.types.LogicArray("0"))

class Handle:
    def __init__(self, width):
        self.width = width
        self.value = 0

    def __len__(self):
        return self.width

def test_is_a_base_signal():
    assert isinstance(Bundle(), BaseSignal)

def test_wraps_raw_handles_and_keeps_adapters():
    handle, constant = Handle(8), Constant(1)
    bundle = Bundle(handle, constant)
    handle.value = 5
    assert bundle.value == (5, 1)

def test_random_value_randomizes_each_signal_and_keeps_constants():
    values = [Bundle(Handle(1), Constant(5), Handle(8)).random_value() for _ in range(200)]
    assert {first for first, _, _ in values} == {0, 1}
    assert {constant for _, constant, _ in values} == {5}
    assert all(0 <= third < 2 ** 8 for _, _, third in values)

def test_random_value_recurses_into_nested_bundles():
    assert Bundle(Bundle(Constant(1), Constant(2)), Constant(3)).random_value() == ((1, 2), 3)

def test_random_value_can_be_driven_back_onto_the_bundle():
    bundle = Bundle(Handle(4), Constant(1))
    bundle.value = bundle.random_value()

def test_random_value_follows_the_global_seed():
    bundle = Bundle(Handle(32), Handle(32))
    random.seed(3)
    first = bundle.random_value()
    random.seed(3)
    assert bundle.random_value() == first
