import collections

import pyuvm

from vulcan_eda.uvm.agents.agent import Agent
from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig

class RecordingSequencer(pyuvm.uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = []

    async def start_item(self, item):
        pass

    async def finish_item(self, item):
        self.items.append(item)

class UpperSequencer(pyuvm.uvm_component):
    class Drained(Exception):
        pass

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = collections.deque()
        self.done_items = []
        self.responses = []
        self.seq_item_export = self

    async def get_next_item(self):
        if not self.items:
            raise UpperSequencer.Drained()
        self._current_item = self.items.popleft()
        return self._current_item

    def item_done(self, rsp=None):
        self.done_items.append(self._current_item)
        if rsp is not None:
            self.responses.append(rsp)

class ScriptedDriver:
    class Drained(Exception):
        pass

    def __init__(self, interface, script):
        self.interface = interface
        self.script = collections.deque(script)

    async def next(self):
        return self._pop()

    async def try_next(self):
        return self._pop()

    async def drive(self, data):
        await self.interface.drive_data(data)

    def _pop(self):
        if not self.script:
            raise ScriptedDriver.Drained()
        return self.script.popleft()

class RecordingSubscriber(pyuvm.uvm_subscriber):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = []

    def write(self, item):
        self.items.append(item)

def create_agent(parent, name, interface, is_active=pyuvm.uvm_active_passive_enum.UVM_ACTIVE):
    AgentConfig(interface, is_active).set(parent, name)
    return Agent.create(name, parent)
