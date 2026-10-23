import types

import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiReadData, AxiResponse

def test_defaults_to_last_beat_with_id_zero():
    read_data = AxiReadData(0x12345678, AxiResponse.OKAY)
    assert (read_data.last, read_data.id) == (True, 0)

def test_to_values_encodes_response():
    assert AxiReadData(0x12345678, AxiResponse.SLVERR, last=False, id=5).to_values() == (5, 0x12345678, 2, False)

def test_from_values_decodes_cocotb_values():
    values = (cocotb.types.LogicArray(5, 4), cocotb.types.LogicArray(0x12345678, 32), cocotb.types.LogicArray(2, 2), cocotb.types.Logic("0"))
    assert AxiReadData.from_values(values) == AxiReadData(0x12345678, AxiResponse.SLVERR, last=False, id=5)

def test_from_values_rejects_unknown_response():
    with pytest.raises(ValueError):
        AxiReadData.from_values((0, 0, 4, 1))

def test_identity_invariant():
    read_data = AxiReadData(0x12345678, AxiResponse.DECERR, last=False, id=3)
    assert AxiReadData.from_values(read_data.to_values()) == read_data

def signal(value=None):
    return types.SimpleNamespace(value=value)

def test_signals_follow_value_order():
    assert AxiReadData.signals(last=signal(3), response=signal(2), data=signal(1), id=signal(0)).value == (0, 1, 2, 3)

def test_signals_default_to_a_lite_read_data():
    signals = AxiReadData.signals(data=signal(), response=signal())
    read_data = AxiReadData(0x12, AxiResponse.DECERR)
    signals.value = read_data.to_values()
    assert AxiReadData.from_values(signals.value) == read_data

def test_signals_reject_a_non_last_beat_on_lite_defaults():
    signals = AxiReadData.signals(data=signal(), response=signal())
    with pytest.raises(ValueError):
        signals.value = AxiReadData(0x12, AxiResponse.OKAY, last=False).to_values()
