import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiBurst

@pytest.mark.parametrize("value, burst", [
    (0, AxiBurst.FIXED),
    (1, AxiBurst.INCR),
    (2, AxiBurst.WRAP),
])
def test_decodes_protocol_encoding(value, burst):
    assert AxiBurst(value) is burst

def test_rejects_reserved_encoding():
    with pytest.raises(ValueError):
        AxiBurst(3)
