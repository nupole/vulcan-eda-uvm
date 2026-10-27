import asyncio

import vulcan_eda.uvm

from tests.support.signals import Handle

class DataInterface(vulcan_eda.uvm.interfaces.base_data_interface.BaseDataInterface):
    async def get_data(self):
        ...

def test_reads_and_writes_a_raw_pin():
    handle = Handle(8)
    data_interface = DataInterface(handle)
    data_interface.write_data(3)
    assert (handle.value, data_interface.read_data()) == (3, 3)

def test_drive_data_writes_the_pin():
    handle = Handle(8)
    asyncio.run(DataInterface(handle).drive_data(3))
    assert handle.value == 3

def test_idle_holds_the_pin_by_default():
    handle = Handle(8)
    data_interface = DataInterface(handle)
    data_interface.write_data(3)
    asyncio.run(data_interface.drive_idle())
    assert handle.value == 3

def test_idle_drives_its_idle_generator():
    handle = Handle(8)
    data_interface = DataInterface(handle, vulcan_eda.uvm.generators.IterableGenerator((4, 5)))
    data_interface.write_idle()
    first = handle.value
    data_interface.write_idle()
    assert (first, handle.value) == (4, 5)

def test_keeps_signal_adapters():
    assert DataInterface(vulcan_eda.uvm.signals.Constant(1)).read_data() == 1
