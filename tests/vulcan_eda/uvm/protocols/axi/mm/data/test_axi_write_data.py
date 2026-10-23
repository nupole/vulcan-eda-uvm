import cocotb.types

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
