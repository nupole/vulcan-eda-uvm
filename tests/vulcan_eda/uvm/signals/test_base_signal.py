import pytest

from vulcan_eda.uvm.signals import BaseSignal

class ValueOnlySignal(BaseSignal):
    @property
    def value(self):
        return 0

class ValueAndChangeSignal(ValueOnlySignal):
    @property
    def value_change(self):
        return None

class CompleteSignal(ValueAndChangeSignal):
    def random_value(self):
        return 1

def test_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseSignal()

def test_requires_value_change():
    with pytest.raises(TypeError):
        ValueOnlySignal()

def test_requires_random_value():
    with pytest.raises(TypeError):
        ValueAndChangeSignal()

def test_subclass_with_value_value_change_and_random_value_can_be_instantiated():
    assert CompleteSignal().random_value() == 1
