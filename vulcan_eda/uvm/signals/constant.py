class Constant:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            raise ValueError(f"cannot drive {value} onto constant {self._value}")
