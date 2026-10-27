import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig
from vulcan_eda.uvm.drivers.driver import Driver
from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem
from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem

class Stop(Exception):
    pass

class Interface:
    def __init__(self, edges):
        self.edges = edges
        self.cycles = []

    async def write_edge(self):
        if self.edges == 0:
            raise Stop()
        self.edges -= 1

    async def drive_data(self, data):
        self.cycles.append(data)

    async def drive_idle(self):
        self.cycles.append("idle")

class Ready:
    async def wait(self):
        pass

class SequenceItemPort:
    def __init__(self, sequence_items):
        self.sequence_items = list(sequence_items)
        self.done = 0
        for sequence_item in self.sequence_items:
            sequence_item.item_ready = Ready()

    def try_next_item(self):
        if self.sequence_items:
            return True, self.sequence_items.pop(0)
        return False, None

    def item_done(self):
        self.done += 1

def create_driver(edges):
    AgentConfig(Interface(edges)).set(None, "driver")
    driver = Driver.create("driver", None)
    driver.build_phase()
    return driver

def run_driver(driver, sequence_items):
    driver.seq_item_port = SequenceItemPort(sequence_items)
    with pytest.raises(Stop):
        asyncio.run(driver.run_phase())

def run(sequence_items, edges):
    driver = create_driver(edges)
    run_driver(driver, sequence_items)
    return driver._interface.cycles, driver.seq_item_port.done

def test_idles_on_every_edge_without_items():
    assert run([], 3) == (["idle", "idle", "idle"], 0)

def test_drives_items_on_consecutive_edges_then_idles():
    assert run([DataSequenceItem("item", 1), DataSequenceItem("item", 2)], 3) == ([1, 2, "idle"], 2)

def test_idles_for_an_idle_item():
    assert run([DataSequenceItem("item", 1), IdleSequenceItem("idle"), DataSequenceItem("item", 2)], 3) == ([1, "idle", 2], 3)

def reported_messages(caplog, driver, sequence_items):
    driver.logger.addHandler(caplog.handler)
    try:
        run_driver(driver, sequence_items)
        driver.report_phase()
    finally:
        driver.logger.removeHandler(caplog.handler)
    return [record.getMessage() for record in caplog.records]

def test_reports_a_summary_of_driven_items(caplog):
    driver = create_driver(3)
    assert reported_messages(caplog, driver, [DataSequenceItem("item", 1), IdleSequenceItem("idle")]) == ["[SUMMARY] drove 1 item(s)"]

def test_reports_driven_items_at_high_verbosity(caplog):
    driver = create_driver(3)
    driver.set_report_verbosity(pyuvm.UVM_HIGH)
    assert reported_messages(caplog, driver, [DataSequenceItem("item", 1), IdleSequenceItem("idle"), DataSequenceItem("item", 2)]) == ["[DROVE] drove 1", "[DROVE] drove 2", "[SUMMARY] drove 2 item(s)"]
