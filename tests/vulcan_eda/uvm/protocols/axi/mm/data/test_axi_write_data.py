import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiWriteData

from tests.support.signals import Handle

def test_defaults_to_last_beat():
    assert AxiWriteData(data=0x12345678, strobe=0xF).last

def test_to_values():
    assert AxiWriteData(data=0x12345678, strobe=0x3, last=False).to_values() == (0x12345678, 0x3, False)

def test_from_values_decodes_cocotb_values():
    values = (cocotb.types.LogicArray(0x12345678, 32), cocotb.types.LogicArray(0x3, 4), cocotb.types.Logic("1"))
    assert AxiWriteData.from_values(values) == AxiWriteData(data=0x12345678, strobe=0x3, last=True)

def test_identity_invariant():
    write_data = AxiWriteData(data=0x12345678, strobe=0x5, last=False)
    assert AxiWriteData.from_values(write_data.to_values()) == write_data

def test_signals_follow_value_order():
    assert AxiWriteData.signals(last=Handle(32, 2), strobe=Handle(32, 1), data=Handle(32, 0)).value == (0, 1, 2)

def test_signals_default_to_a_lite_write_data():
    signals = AxiWriteData.signals(data=Handle(32), strobe=Handle(32))
    write_data = AxiWriteData(data=0xAB, strobe=0xF)
    signals.value = write_data.to_values()
    assert AxiWriteData.from_values(signals.value) == write_data

def test_signals_reject_a_non_last_beat_on_lite_defaults():
    signals = AxiWriteData.signals(data=Handle(32), strobe=Handle(32))
    with pytest.raises(ValueError):
        signals.value = AxiWriteData(data=0xAB, strobe=0xF, last=False).to_values()

def test_is_keyword_only():
    with pytest.raises(TypeError):
        AxiWriteData(0xAB, 0xF)

def test_prints_data_and_strobe_in_hex():
    assert str(AxiWriteData(data=0xdeadbeef, strobe=0xf)) == "AxiWriteData(data=0xdeadbeef, strobe=0xf, last=True)"
