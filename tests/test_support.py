import asyncio

import pytest
import pyuvm

import vulcan_eda.uvm

from tests.support.components import ScriptedDriver, create_agent
from tests.support.generators import take
from tests.support.signals import Handle

def test_handle_has_a_width_and_a_value():
    handle = Handle(8, value=5)
    assert (len(handle), handle.value) == (8, 5)

def test_take_returns_the_first_values():
    assert take(iter(range(10)), 3) == [0, 1, 2]

def test_create_agent_configures_and_creates_an_agent():
    parent = pyuvm.uvm_component("parent", None)
    interface = vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, Handle(8))
    agent = create_agent(parent, "agent", interface, pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
    assert (agent.get_name(), vulcan_eda.uvm.configs.agents.AgentConfig.get(agent).is_active) == ("agent", pyuvm.uvm_active_passive_enum.UVM_PASSIVE)

def test_scripted_driver_hands_out_its_script_then_drains():
    scripted_driver = ScriptedDriver(None, [1, None])
    assert (asyncio.run(scripted_driver.next()), asyncio.run(scripted_driver.try_next())) == (1, None)
    with pytest.raises(ScriptedDriver.Drained):
        asyncio.run(scripted_driver.try_next())

def test_scripted_driver_drives_data_onto_its_interface():
    handle = Handle(8)
    asyncio.run(ScriptedDriver(vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, handle), []).drive(5))
    assert handle.value == 5
