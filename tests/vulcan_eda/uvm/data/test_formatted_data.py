import dataclasses
import enum

import pytest

from vulcan_eda.uvm.data import FormattedData

class Color(enum.Enum):
    RED = 1

@dataclasses.dataclass(frozen=True, kw_only=True)
class Inner(FormattedData):
    value: int | None = dataclasses.field(metadata={"format": "#x"})

@dataclasses.dataclass(frozen=True, kw_only=True)
class Outer(FormattedData):
    class Kind(enum.Enum):
        WRITE = 1

    kind: Kind = Kind.WRITE
    address: int = dataclasses.field(default=255, metadata={"format": "#x"})
    count: int = 255
    color: Color | None = None
    inner: Inner = Inner(value=16)
    hidden: int = dataclasses.field(default=0, repr=False)

@dataclasses.dataclass(frozen=True, kw_only=True)
class Words(FormattedData):
    data: tuple[int, ...] = dataclasses.field(metadata={"format": "#x"})

@dataclasses.dataclass(frozen=True, kw_only=True)
class Packet(FormattedData):
    data: bytes = dataclasses.field(metadata={"format": "#x"})

def test_formats_fields_by_their_format():
    assert str(Outer(color=Color.RED)) == "Outer(kind=WRITE, address=0xff, count=255, color=RED, inner=Inner(value=0x10))"

@pytest.mark.parametrize("data, formatted", [
    ((), "Words(data=())"),
    ((10,), "Words(data=(0xa,))"),
    ((10, 11), "Words(data=(0xa, 0xb))"),
])
def test_formats_each_element_of_a_tuple(data, formatted):
    assert str(Words(data=data)) == formatted

def test_formats_bytes_as_hex_keeping_every_byte():
    assert str(Packet(data=bytes([0x00, 0x01, 0xa0, 0xff]))) == "Packet(data=0x0001a0ff)"

def test_formats_none_without_a_format():
    assert str(Inner(value=None)) == "Inner(value=None)"

def test_keeps_the_exact_repr():
    assert repr(Inner(value=16)) == "Inner(value=16)"
