import types

import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiWriteData

def test_defaults_to_last_beat():
    assert AxiWriteData(0x12345678, 0xF).last

def test_to_values():
    assert AxiWriteData(0x12345678, 0x3, last=False).to_values() == (0x12345678, 0x3, False)

def test_from_values_decodes_cocotb_values():
    values = (cocotb.types.LogicArray(0x12345678, 32), cocotb.types.LogicArray(0x3, 4), cocotb.types.Logic("1"))
    assert AxiWriteData.from_values(values) == AxiWriteData(0x12345678, 0x3, last=True)

def test_identity_invariant():
    write_data = AxiWriteData(0x12345678, 0x5, last=False)
    assert AxiWriteData.from_values(write_data.to_values()) == write_data

def signal(value=None):
    return types.SimpleNamespace(value=value)

def test_signals_follow_value_order():
    assert AxiWriteData.signals(last=signal(2), strobe=signal(1), data=signal(0)).value == (0, 1, 2)

def test_signals_default_to_a_lite_write_data():
    signals = AxiWriteData.signals(data=signal(), strobe=signal())
    write_data = AxiWriteData(0xAB, 0xF)
    signals.value = write_data.to_values()
    assert AxiWriteData.from_values(signals.value) == write_data

def test_signals_reject_a_non_last_beat_on_lite_defaults():
    signals = AxiWriteData.signals(data=signal(), strobe=signal())
    with pytest.raises(ValueError):
        signals.value = AxiWriteData(0xAB, 0xF, last=False).to_values()
