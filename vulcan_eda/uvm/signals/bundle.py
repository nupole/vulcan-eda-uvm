class Bundle:
    def __init__(self, *signals):
        self._signals = signals

    @property
    def value(self):
        return tuple(signal.value for signal in self._signals)

    @value.setter
    def value(self, values):
        for signal, value in zip(self._signals, values, strict=True):
            signal.value = value
