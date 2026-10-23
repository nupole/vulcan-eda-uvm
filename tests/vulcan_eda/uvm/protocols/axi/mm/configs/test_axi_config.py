import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig

def test_from_pins():
    config = AxiConfig.from_pins(AxiConfig.Profile.LITE, cocotb.types.LogicArray(0, 32), cocotb.types.LogicArray(0, 12))
    assert config == AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=4, address_width=12)

def test_from_pins_rejects_partial_byte():
    with pytest.raises(ValueError):
        AxiConfig.from_pins(AxiConfig.Profile.LITE, cocotb.types.LogicArray(0, 30), cocotb.types.LogicArray(0, 12))

def test_requires_all_fields():
    with pytest.raises(TypeError):
        AxiConfig(AxiConfig.Profile.LITE)

@pytest.mark.parametrize("bytes_per_beat", [4, 8])
def test_lite_accepts_32_and_64_bit_data(bytes_per_beat):
    AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=bytes_per_beat, address_width=12)

@pytest.mark.parametrize("bytes_per_beat", [2, 16])
def test_lite_rejects_other_data_widths(bytes_per_beat):
    with pytest.raises(ValueError):
        AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=bytes_per_beat, address_width=12)

def test_rejects_bytes_per_beat_not_a_power_of_two():
    with pytest.raises(ValueError):
        AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=6, address_width=12)

def test_rejects_address_width_not_positive():
    with pytest.raises(ValueError):
        AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=4, address_width=0)
