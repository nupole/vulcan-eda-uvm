import asyncio

import pytest

import vulcan_eda.uvm

from tests.support.components import ScriptedDriver

class RecordingInterface(vulcan_eda.uvm.interfaces.SynchronousInterface):
    def __init__(self):
        super().__init__(None)
        self.events = []

    async def write_edge(self):
        self.events.append("write_edge")

    async def drive_data(self, data):
        self.events.append(data)

    async def drive_idle(self):
        self.events.append("idle")

    async def get_data(self):
        ...

def run(script):
    recording_interface = RecordingInterface()
    with pytest.raises(ScriptedDriver.Drained):
        asyncio.run(recording_interface.run(ScriptedDriver(recording_interface, script)))
    return recording_interface.events

def test_idles_on_every_edge_without_items():
    assert run([None, None]) == ["write_edge", "idle", "write_edge", "idle", "write_edge"]

def test_drives_items_on_consecutive_edges_then_idles():
    assert run([1, 2, None]) == ["write_edge", 1, "write_edge", 2, "write_edge", "idle", "write_edge"]

def test_base_interface_has_no_clock():
    assert not hasattr(vulcan_eda.uvm.interfaces.base_interface.BaseInterface, "write_edge")
