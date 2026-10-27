import cocotb

from vulcan_eda.uvm.signals.base_signal import BaseSignal
from vulcan_eda.uvm.signals.signal import Signal

class Bundle(BaseSignal):
    def __init__(self, *signals):
        self._signals = tuple(Signal.wrap(signal) for signal in signals)

    @property
    def value(self):
        return tuple(signal.value for signal in self._signals)

    @value.setter
    def value(self, values):
        for signal, value in zip(self._signals, values, strict=True):
            signal.value = value

    @property
    def value_change(self):
        return cocotb.triggers.First(*(signal.value_change for signal in self._signals))

    def random_value(self):
        return tuple(signal.random_value() for signal in self._signals)
