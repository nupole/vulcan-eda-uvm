import random

from vulcan_eda.uvm.signals import BaseSignal, Constant, Signal

class Handle:
    def __init__(self, width, value=0):
        self.width = width
        self.value = value

    def __len__(self):
        return self.width

def test_is_a_base_signal():
    assert isinstance(Signal(Handle(8)), BaseSignal)

def test_value_reads_the_handle():
    assert Signal(Handle(8, value=5)).value == 5

def test_value_drives_the_handle():
    handle = Handle(8)
    Signal(handle).value = 7
    assert handle.value == 7

def test_len_is_the_handle_width():
    assert len(Signal(Handle(12))) == 12

def test_random_value_covers_its_width():
    signal = Signal(Handle(2))
    assert {signal.random_value() for _ in range(200)} == {0, 1, 2, 3}

def test_random_value_uses_the_top_bit_of_wide_handles():
    signal = Signal(Handle(512))
    assert any(signal.random_value() >> 511 for _ in range(100))

def test_random_value_follows_the_global_seed():
    signal = Signal(Handle(32))
    random.seed(3)
    first = signal.random_value()
    random.seed(3)
    assert signal.random_value() == first

def test_wrap_wraps_a_raw_handle():
    handle = Handle(8, value=5)
    signal = Signal.wrap(handle)
    assert isinstance(signal, Signal) and signal.value == 5

def test_wrap_returns_base_signals_unchanged():
    constant = Constant(1)
    assert Signal.wrap(constant) is constant

def test_wrap_does_not_double_wrap():
    signal = Signal(Handle(8))
    assert Signal.wrap(signal) is signal
