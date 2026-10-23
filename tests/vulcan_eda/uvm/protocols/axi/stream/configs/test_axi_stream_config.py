import cocotb.types
import pytest

from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig

def test_num_bytes():
    assert AxiStreamConfig(num_bytes=4).num_bytes == 4

def test_from_tdata():
    assert AxiStreamConfig.from_tdata(cocotb.types.LogicArray(0, 32)) == AxiStreamConfig(num_bytes=4)

def test_from_tdata_rejects_partial_byte():
    with pytest.raises(ValueError):
        AxiStreamConfig.from_tdata(cocotb.types.LogicArray(0, 12))

def test_requires_num_bytes():
    with pytest.raises(TypeError):
        AxiStreamConfig()

@pytest.mark.parametrize("num_bytes", [-1, 0])
def test_rejects_num_bytes_not_positive(num_bytes):
    with pytest.raises(ValueError):
        AxiStreamConfig(num_bytes=num_bytes)
