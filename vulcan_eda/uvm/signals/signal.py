import random

from vulcan_eda.uvm.signals.base_signal import BaseSignal

class Signal(BaseSignal):
    def __init__(self, handle):
        self._handle = handle

    @property
    def value(self):
        return self._handle.value

    @value.setter
    def value(self, value):
        self._handle.value = value

    def __len__(self):
        return len(self._handle)

    def random_value(self):
        return random.getrandbits(len(self._handle))

    @classmethod
    def wrap(cls, signal):
        if isinstance(signal, BaseSignal):
            return signal
        return cls(signal)
