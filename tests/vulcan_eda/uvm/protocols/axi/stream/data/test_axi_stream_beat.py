import types

import cocotb.types

from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat

def test_to_values():
    assert AxiStreamBeat(0x12, True).to_values() == (0x12, True)

def test_from_values():
    values = (cocotb.types.LogicArray("00010010"), cocotb.types.Logic("1"))
    assert AxiStreamBeat.from_values(values) == AxiStreamBeat(0x12, True)

def test_identity_invariant():
    beat = AxiStreamBeat(0x12, True)
    assert AxiStreamBeat.from_values(beat.to_values()) == beat

def test_signals_follow_value_order():
    data, last = types.SimpleNamespace(value=0x12), types.SimpleNamespace(value=True)
    assert AxiStreamBeat.signals(last=last, data=data).value == AxiStreamBeat(0x12, True).to_values()
