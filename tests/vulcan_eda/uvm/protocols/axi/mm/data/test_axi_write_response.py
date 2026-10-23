import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiResponse, AxiWriteResponse

def test_defaults_to_id_zero():
    assert AxiWriteResponse(AxiResponse.OKAY).id == 0

def test_to_values_encodes_response():
    assert AxiWriteResponse(AxiResponse.SLVERR, id=5).to_values() == (5, 2)

def test_from_values_decodes_cocotb_values():
    values = (cocotb.types.LogicArray(5, 4), cocotb.types.LogicArray(2, 2))
    assert AxiWriteResponse.from_values(values) == AxiWriteResponse(AxiResponse.SLVERR, id=5)

def test_from_values_rejects_unknown_response():
    with pytest.raises(ValueError):
        AxiWriteResponse.from_values((0, 4))

def test_identity_invariant():
    write_response = AxiWriteResponse(AxiResponse.DECERR, id=3)
    assert AxiWriteResponse.from_values(write_response.to_values()) == write_response
