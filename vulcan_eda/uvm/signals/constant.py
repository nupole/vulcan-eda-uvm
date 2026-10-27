import cocotb

from vulcan_eda.uvm.signals.base_signal import BaseSignal

class Constant(BaseSignal):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            raise ValueError(f"cannot drive {value} onto constant {self._value}")

    @property
    def value_change(self):
        return cocotb.triggers.Event().wait()

    def random_value(self):
        return self._value
