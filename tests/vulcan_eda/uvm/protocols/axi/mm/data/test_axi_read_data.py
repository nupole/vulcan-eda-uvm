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
