import types

import cocotb.types
import pytest

from vulcan_eda.uvm.signals.bundle import Bundle

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
