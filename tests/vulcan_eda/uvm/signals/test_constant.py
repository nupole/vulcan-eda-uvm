import cocotb.types
import pytest

from vulcan_eda.uvm.signals.constant import Constant

def test_value_reads_constant():
    assert Constant(0xF).value == 0xF

def test_value_accepts_driving_constant():
    constant = Constant(0xF)
    constant.value = 0xF
    assert constant.value == 0xF

def test_value_accepts_driving_equal_logic_array():
    constant = Constant(0xF)
    constant.value = cocotb.types.LogicArray("1111")
    assert constant.value == 0xF

def test_value_rejects_driving_different_value():
    with pytest.raises(ValueError):
        Constant(0xF).value = 0x7
