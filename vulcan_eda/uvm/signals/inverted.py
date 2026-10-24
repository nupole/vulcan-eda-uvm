from vulcan_eda.uvm.signals.base_signal import BaseSignal
from vulcan_eda.uvm.signals.signal import Signal

class Inverted(BaseSignal):
    def __init__(self, signal):
        self._signal = Signal.wrap(signal)
        self._mask = 2 ** len(self._signal) - 1

    @property
    def value(self):
        return self._invert(self._signal.value)

    @value.setter
    def value(self, value):
        self._signal.value = self._invert(value)

    def __len__(self):
        return len(self._signal)

    def random_value(self):
        return self._invert(self._signal.random_value())

    def _invert(self, value):
        if isinstance(value, int):
            return value ^ self._mask
        return ~value
