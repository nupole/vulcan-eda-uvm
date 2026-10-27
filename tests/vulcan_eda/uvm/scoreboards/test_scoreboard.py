import asyncio
import collections
import dataclasses
import logging

import cocotb.types
import pytest
import pyuvm

from vulcan_eda.uvm.configs.tests import VerdictConfig
from vulcan_eda.uvm.scoreboards import Scoreboard

class DrainingFifo:
    class Drained(Exception):
        pass

    def __init__(self, items):
        self.items = collections.deque(items)

    async def peek(self):
        if not self.items:
            raise DrainingFifo.Drained()
        return self.items[0]

    async def get(self):
        item = await self.peek()
        self.items.popleft()
        return item

    def try_get(self):
        return True, self.items.popleft()

    def is_empty(self):
        return not self.items

    def used(self):
        return len(self.items)

@dataclasses.dataclass(frozen=True, kw_only=True)
class Transfer:
    address: int
    data: int
    last: bool

@pytest.fixture
def scoreboard(caplog):
    scoreboard = Scoreboard.create("scoreboard", None)
    scoreboard.build_phase()
    scoreboard.logger.addHandler(caplog.handler)
    yield scoreboard
    scoreboard.logger.removeHandler(caplog.handler)

def run(scoreboard, actual_data, expected_data):
    scoreboard.actual_data_analysis_fifo = DrainingFifo(actual_data)
    scoreboard.expected_data_analysis_fifo = DrainingFifo(expected_data)
    with pytest.raises(DrainingFifo.Drained):
        asyncio.run(scoreboard.run_phase())

def messages(caplog, level):
    return [record.getMessage() for record in caplog.records if record.levelno == level]

def mismatch(actual_text, expected_text):
    return f"[MISMATCHED] actual data does not equal expected data\nactual:   {actual_text}\nexpected: {expected_text}"

def test_passes_when_all_data_matches(scoreboard, caplog):
    run(scoreboard, [1, 2], [1, 2])
    scoreboard.check_phase()
    assert messages(caplog, logging.INFO) == ["[SUMMARY] compared 2: 2 matched, 0 mismatched"]

def test_reports_matches_at_high_verbosity(scoreboard, caplog):
    scoreboard.set_report_verbosity(pyuvm.UVM_HIGH)
    run(scoreboard, [1, 2], [1, 2])
    assert messages(caplog, logging.INFO) == ["[MATCHED] matched 1", "[MATCHED] matched 2"]

def test_reports_every_mismatch(scoreboard, caplog):
    run(scoreboard, [1, 2, 3], [9, 2, 8])
    scoreboard.check_phase()
    assert messages(caplog, logging.ERROR) == [mismatch("1", "9"), mismatch("3", "8")]
    assert messages(caplog, logging.INFO) == ["[SUMMARY] compared 3: 1 matched, 2 mismatched"]

@pytest.mark.parametrize("kind, actual_data, expected_data", [
    ("actual", [1, 2], [1]),
    ("expected", [1], [1, 2]),
])
def test_reports_data_never_compared(scoreboard, caplog, kind, actual_data, expected_data):
    run(scoreboard, actual_data, expected_data)
    scoreboard.check_phase()
    assert messages(caplog, logging.ERROR) == [f"[UNCOMPARED] 1 {kind} data never compared"]

def test_warns_when_nothing_was_compared(scoreboard, caplog):
    scoreboard.check_phase()
    assert messages(caplog, logging.WARNING) == ["[NOTHING_COMPARED] compared nothing"]

def test_accepts_a_base_test_ancestor(base_test):
    environment = pyuvm.uvm_env("env", base_test())
    Scoreboard.create("scoreboard", environment).end_of_elaboration_phase()

def test_accepts_any_test_that_owns_the_verdict():
    test = pyuvm.uvm_test("uvm_test_top", None)
    VerdictConfig(test).set(test, "*")
    Scoreboard.create("scoreboard", pyuvm.uvm_env("env", test)).end_of_elaboration_phase()

def test_requires_a_verdict_owner():
    environment = pyuvm.uvm_env("env", pyuvm.uvm_test("uvm_test_top", None))
    with pytest.raises(pyuvm.UVMError, match="BaseTest"):
        Scoreboard.create("scoreboard", environment).end_of_elaboration_phase()

@pytest.mark.parametrize("actual_data, expected_data, actual_text, expected_text", [
    (cocotb.types.LogicArray("00000111"), 6, "0x07", "0x06"),
    (cocotb.types.LogicArray("0000X111"), 7, "0b0000X111", "0b00000111"),
    ((cocotb.types.Logic("1"), cocotb.types.LogicArray("0101")), (0, 5), "(0x1, 0x5)", "(0x0, 0x5)"),
    ((cocotb.types.LogicArray("0011"),), (2,), "(0x3,)", "(0x2,)"),
    (cocotb.types.LogicArray("0011"), -1, "0011", "-1"),
])
def test_reports_a_mismatch_in_one_format_for_both_sides(scoreboard, caplog, actual_data, expected_data, actual_text, expected_text):
    run(scoreboard, [actual_data], [expected_data])
    assert messages(caplog, logging.ERROR) == [mismatch(actual_text, expected_text)]

def test_names_the_fields_that_differ(scoreboard, caplog):
    run(scoreboard, [Transfer(address=1, data=2, last=True)], [Transfer(address=1, data=3, last=False)])
    assert messages(caplog, logging.ERROR) == [mismatch("Transfer(address=1, data=2, last=True)", "Transfer(address=1, data=3, last=False)") + "\ndiffers in: data, last"]

def test_reports_matches_in_the_shared_format(scoreboard, caplog):
    scoreboard.set_report_verbosity(pyuvm.UVM_HIGH)
    run(scoreboard, [cocotb.types.LogicArray("00000111")], [7])
    assert messages(caplog, logging.INFO) == ["[MATCHED] matched 0x07"]
