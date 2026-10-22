import pytest

from vulcan_eda.uvm.configs.axi.stream import AxiStreamConfig

def test_num_bytes():
    assert AxiStreamConfig(num_bytes=4).num_bytes == 4

def test_requires_num_bytes():
    with pytest.raises(TypeError):
        AxiStreamConfig()

@pytest.mark.parametrize("num_bytes", [-1, 0])
def test_rejects_num_bytes_not_positive(num_bytes):
    with pytest.raises(ValueError):
        AxiStreamConfig(num_bytes=num_bytes)
