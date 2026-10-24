import dataclasses

import cocotb.simtime
import pytest

from vulcan_eda.uvm.generators import TimeGenerator

from tests.support.generators import take

@pytest.fixture
def sim_time(monkeypatch):
    calls = []
    def get_sim_time(unit):
        calls.append(unit)
        return 12.75 * len(calls)
    monkeypatch.setattr(cocotb.simtime, "get_sim_time", get_sim_time)
    return calls

def test_reads_simulation_time_on_every_value(sim_time):
    assert take(TimeGenerator(), 2) == [12, 25]

def test_defaults_to_ns(sim_time):
    take(TimeGenerator(), 1)
    assert sim_time == ["ns"]

def test_uses_the_chosen_unit(sim_time):
    take(TimeGenerator(unit="ps"), 1)
    assert sim_time == ["ps"]

def test_rejects_unknown_unit():
    with pytest.raises(ValueError):
        TimeGenerator(unit="minutes")

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        TimeGenerator().unit = "ps"

def test_repr_shows_its_unit():
    assert repr(TimeGenerator(unit="us")) == "TimeGenerator(unit='us')"
