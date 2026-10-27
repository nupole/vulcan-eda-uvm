import asyncio

import vulcan_eda.uvm

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

def test_put_data_drives_after_the_write_edge():
    recording_interface = RecordingInterface()
    asyncio.run(recording_interface.put_data(5))
    assert recording_interface.events == ["write_edge", 5]

def test_put_idle_drives_idle_after_the_write_edge():
    recording_interface = RecordingInterface()
    asyncio.run(recording_interface.put_idle())
    assert recording_interface.events == ["write_edge", "idle"]

def test_base_interface_has_no_clock():
    assert not hasattr(vulcan_eda.uvm.interfaces.base_interface.BaseInterface, "write_edge")
