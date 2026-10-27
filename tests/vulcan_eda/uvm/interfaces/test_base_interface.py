import asyncio

import pytest

from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

from tests.support.components import ScriptedDriver

class RecordingInterface(BaseInterface):
    def __init__(self):
        self.events = []

    async def drive_data(self, data):
        self.events.append(data)

    async def drive_idle(self):
        self.events.append("idle")

    async def get_data(self):
        ...

def test_idles_once_then_drives_each_item_as_it_arrives():
    recording_interface = RecordingInterface()
    with pytest.raises(ScriptedDriver.Drained):
        asyncio.run(recording_interface.run(ScriptedDriver(recording_interface, [1, 2])))
    assert recording_interface.events == ["idle", 1, 2]
