import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiResponse, AxiWriteResponse

from tests.support.signals import Handle

def test_defaults_to_id_zero():
    assert AxiWriteResponse(response=AxiResponse.OKAY).id == 0

def test_to_values_encodes_response():
    assert AxiWriteResponse(response=AxiResponse.SLVERR, id=5).to_values() == (5, 2)

def test_from_values_decodes_cocotb_values():
    values = (cocotb.types.LogicArray(5, 4), cocotb.types.LogicArray(2, 2))
    assert AxiWriteResponse.from_values(values) == AxiWriteResponse(response=AxiResponse.SLVERR, id=5)

def test_from_values_rejects_unknown_response():
    with pytest.raises(ValueError):
        AxiWriteResponse.from_values((0, 4))

def test_identity_invariant():
    write_response = AxiWriteResponse(response=AxiResponse.DECERR, id=3)
    assert AxiWriteResponse.from_values(write_response.to_values()) == write_response

def test_signals_follow_value_order():
    assert AxiWriteResponse.signals(response=Handle(32, 1), id=Handle(32, 0)).value == (0, 1)

def test_signals_default_to_a_lite_write_response():
    signals = AxiWriteResponse.signals(response=Handle(32))
    write_response = AxiWriteResponse(response=AxiResponse.SLVERR)
    signals.value = write_response.to_values()
    assert AxiWriteResponse.from_values(signals.value) == write_response

def test_signals_reject_an_id_on_lite_defaults():
    signals = AxiWriteResponse.signals(response=Handle(32))
    with pytest.raises(ValueError):
        signals.value = AxiWriteResponse(response=AxiResponse.OKAY, id=1).to_values()

def test_is_keyword_only():
    with pytest.raises(TypeError):
        AxiWriteResponse(AxiResponse.OKAY)
