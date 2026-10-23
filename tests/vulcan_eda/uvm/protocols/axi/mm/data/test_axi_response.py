import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiResponse

@pytest.mark.parametrize("value, response", [
    (0, AxiResponse.OKAY),
    (1, AxiResponse.EXOKAY),
    (2, AxiResponse.SLVERR),
    (3, AxiResponse.DECERR),
])
def test_decodes_protocol_encoding(value, response):
    assert AxiResponse(value) is response

def test_rejects_unknown_encoding():
    with pytest.raises(ValueError):
        AxiResponse(4)
