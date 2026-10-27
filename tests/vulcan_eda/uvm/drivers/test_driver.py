import asyncio

import pyuvm

from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig
from vulcan_eda.uvm.drivers.driver import Driver
from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem
from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem

from tests.support.data import Unprintable

class Interface:
    def __init__(self):
        self.cycles = []
        self.driver = None

    async def run(self, driver):
        self.driver = driver

    async def drive_data(self, data):
        self.cycles.append(data)

    async def drive_idle(self):
        self.cycles.append("idle")

class Ready:
    def __init__(self):
        self.waited = False

    async def wait(self):
        self.waited = True

class SequenceItemPort:
    def __init__(self, sequence_items):
        self.sequence_items = list(sequence_items)
        self.done = 0
        for sequence_item in self.sequence_items:
            sequence_item.item_ready = Ready()

    async def get_next_item(self):
        return self.sequence_items.pop(0)

    def try_next_item(self):
        if self.sequence_items:
            return True, self.sequence_items.pop(0)
        return False, None

    def item_done(self):
        self.done += 1

def create_driver(sequence_items=()):
    AgentConfig(Interface()).set(None, "driver")
    driver = Driver.create("driver", None)
    driver.build_phase()
    driver.seq_item_port = SequenceItemPort(sequence_items)
    return driver

def drive(driver, sequence_items):
    for sequence_item in sequence_items:
        asyncio.run(driver.drive(sequence_item))
    return driver._interface.cycles, driver.seq_item_port.done

def test_run_phase_hands_the_driver_to_its_interface():
    driver = create_driver()
    asyncio.run(driver.run_phase())
    assert driver._interface.driver is driver

def test_next_waits_for_the_next_item():
    sequence_item = DataSequenceItem("item", 1)
    assert asyncio.run(create_driver([sequence_item]).next()) is sequence_item

def test_try_next_returns_none_without_an_item():
    assert asyncio.run(create_driver().try_next()) is None

def test_try_next_waits_until_the_item_is_ready():
    sequence_item = DataSequenceItem("item", 1)
    assert (asyncio.run(create_driver([sequence_item]).try_next()), sequence_item.item_ready.waited) == (sequence_item, True)

def test_drives_data_items_and_finishes_each():
    assert drive(create_driver(), [DataSequenceItem("item", 1), DataSequenceItem("item", 2)]) == ([1, 2], 2)

def test_idles_for_an_idle_item():
    assert drive(create_driver(), [DataSequenceItem("item", 1), IdleSequenceItem("idle"), DataSequenceItem("item", 2)]) == ([1, "idle", 2], 3)

def reported_messages(caplog, driver, sequence_items):
    driver.logger.addHandler(caplog.handler)
    try:
        drive(driver, sequence_items)
        driver.report_phase()
    finally:
        driver.logger.removeHandler(caplog.handler)
    return [record.getMessage() for record in caplog.records]

def test_reports_a_summary_of_driven_items(caplog):
    driver = create_driver()
    assert reported_messages(caplog, driver, [DataSequenceItem("item", 1), IdleSequenceItem("idle")]) == ["[SUMMARY] drove 1 item(s)"]

def test_reports_driven_items_at_high_verbosity(caplog):
    driver = create_driver()
    driver.set_report_verbosity(pyuvm.UVM_HIGH)
    assert reported_messages(caplog, driver, [DataSequenceItem("item", 1), IdleSequenceItem("idle"), DataSequenceItem("item", 2)]) == ["[DROVE] drove 1", "[DROVE] drove 2", "[SUMMARY] drove 2 item(s)"]

def test_formats_no_driven_item_below_high_verbosity():
    assert drive(create_driver(), [DataSequenceItem("item", Unprintable())])[1] == 1
