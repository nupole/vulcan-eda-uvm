class Bundle:
    class Value(tuple):
        @property
        def is_resolvable(self):
            return all(value.is_resolvable for value in self)

    def __init__(self, *signals):
        self._signals = signals

    @property
    def value(self):
        return Bundle.Value(signal.value for signal in self._signals)

    @value.setter
    def value(self, values):
        for signal, value in zip(self._signals, values, strict=True):
            signal.value = value
