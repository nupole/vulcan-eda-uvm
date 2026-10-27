import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat

from tests.support.signals import Handle

def test_to_values():
    assert AxiStreamBeat(data=0x12, last=True).to_values() == (0x12, True)

def test_from_values():
    values = (cocotb.types.LogicArray("00010010"), cocotb.types.Logic("1"))
    assert AxiStreamBeat.from_values(values) == AxiStreamBeat(data=0x12, last=True)

def test_identity_invariant():
    beat = AxiStreamBeat(data=0x12, last=True)
    assert AxiStreamBeat.from_values(beat.to_values()) == beat

def test_signals_follow_value_order():
    data, last = Handle(8, 0x12), Handle(1, True)
    assert AxiStreamBeat.signals(last=last, data=data).value == AxiStreamBeat(data=0x12, last=True).to_values()

def test_is_keyword_only():
    with pytest.raises(TypeError):
        AxiStreamBeat(0x12, True)

def test_prints_data_in_hex():
    assert str(AxiStreamBeat(data=0xff, last=True)) == "AxiStreamBeat(data=0xff, last=True)"
