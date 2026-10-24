import asyncio

import pytest

from vulcan_eda.uvm.drivers.driver import Driver
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
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

def run(sequence_items, edges):
    driver = Driver.create("driver", None)
    driver._interface = Interface(edges)
    driver.seq_item_port = SequenceItemPort(sequence_items)
    with pytest.raises(Stop):
        asyncio.run(driver.run_phase())
    return driver._interface.cycles, driver.seq_item_port.done

def test_idles_on_every_edge_without_items():
    assert run([], 3) == (["idle", "idle", "idle"], 0)

def test_drives_items_on_consecutive_edges_then_idles():
    assert run([DataSequenceItem("item", 1), DataSequenceItem("item", 2)], 3) == ([1, 2, "idle"], 2)

def test_idles_for_an_idle_item():
    assert run([DataSequenceItem("item", 1), IdleSequenceItem("idle"), DataSequenceItem("item", 2)], 3) == ([1, "idle", 2], 3)
