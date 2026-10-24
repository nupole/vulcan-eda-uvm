import pyuvm

import vulcan_eda.uvm

from tests.support.components import create_agent
from tests.support.generators import take
from tests.support.signals import Handle

def test_handle_has_a_width_and_a_value():
    handle = Handle(8, value=5)
    assert (len(handle), handle.value) == (8, 5)

def test_take_returns_the_first_values():
    assert take(iter(range(10)), 3) == [0, 1, 2]

def test_create_agent_configures_and_creates_an_agent():
    parent = pyuvm.uvm_component("parent", None)
    interface = vulcan_eda.uvm.interfaces.DataInterface(None, Handle(8))
    agent = create_agent(parent, "agent", interface, pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
    assert (agent.get_name(), vulcan_eda.uvm.configs.agents.AgentConfig.get(agent).is_active) == ("agent", pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
