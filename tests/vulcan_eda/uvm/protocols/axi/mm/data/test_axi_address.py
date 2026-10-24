import types

import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiAddress, AxiBurst
from vulcan_eda.uvm.signals import Constant

def test_defaults_are_a_single_beat_incr_with_id_and_prot_zero():
    address = AxiAddress(0x10, 4)
    assert (address.num_beats, address.id, address.burst, address.prot) == (1, 0, AxiBurst.INCR, 0)

def test_to_values_encodes_len_and_size():
    assert AxiAddress(0x10, 4, num_beats=8, id=3, burst=AxiBurst.WRAP, prot=2).to_values() == (3, 0x10, 7, 2, 2, 2)

def test_from_values_decodes_cocotb_values():
    values = tuple(cocotb.types.LogicArray(value, 8) for value in (3, 0x10, 7, 2, 2, 2))
    assert AxiAddress.from_values(values) == AxiAddress(0x10, 4, num_beats=8, id=3, burst=AxiBurst.WRAP, prot=2)

def test_identity_invariant():
    address = AxiAddress(0x10, 8, num_beats=256, id=1, burst=AxiBurst.FIXED, prot=7)
    assert AxiAddress.from_values(address.to_values()) == address

@pytest.mark.parametrize("num_beats", [0, 257])
def test_rejects_num_beats_out_of_range(num_beats):
    with pytest.raises(ValueError):
        AxiAddress(0x10, 4, num_beats=num_beats)

@pytest.mark.parametrize("bytes_per_beat", [0, 3])
def test_rejects_bytes_per_beat_not_a_power_of_two(bytes_per_beat):
    with pytest.raises(ValueError):
        AxiAddress(0x10, bytes_per_beat)

def signal(value=None):
    return types.SimpleNamespace(value=value)

def test_signals_follow_value_order():
    pins = {name: signal(value) for value, name in enumerate(("id", "address", "num_beats", "bytes_per_beat", "burst", "prot"))}
    assert AxiAddress.signals(**pins).value == (0, 1, 2, 3, 4, 5)

def test_signals_default_to_a_lite_address():
    signals = AxiAddress.signals(address=signal(), bytes_per_beat=Constant(2), prot=signal())
    address = AxiAddress(0x10, 4, prot=2)
    signals.value = address.to_values()
    assert AxiAddress.from_values(signals.value) == address

def test_signals_reject_a_burst_on_lite_defaults():
    signals = AxiAddress.signals(address=signal(), bytes_per_beat=Constant(2), prot=signal())
    with pytest.raises(ValueError):
        signals.value = AxiAddress(0x10, 4, num_beats=2).to_values()
