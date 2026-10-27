import asyncio
import pathlib

import cocotb
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from tests.support.components import create_agent

class ChangingSignal(vulcan_eda.uvm.signals.BaseSignal):
    def __init__(self, next_value):
        self._value = 0
        self._next_value = next_value

    @property
    def value(self):
        return self._value

    @property
    def value_change(self):
        return self._change()

    def random_value(self):
        return 0

    async def _change(self):
        self._value = self._next_value

def test_get_data_reads_after_the_data_changes():
    assert asyncio.run(vulcan_eda.uvm.interfaces.AsynchronousDataInterface(ChangingSignal(5)).get_data()) == 5

def test_runs_the_untimed_loop():
    assert vulcan_eda.uvm.interfaces.AsynchronousDataInterface.run is vulcan_eda.uvm.interfaces.base_interface.BaseInterface.run

class SpacedDataSequence(vulcan_eda.uvm.sequences.DataSequence):
    async def finish_item(self, item):
        await super().finish_item(item)
        await cocotb.triggers.Timer(10, unit="ns")

class AsynchronousDataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        self.upstream_agent = create_agent(self, "upstream_agent", vulcan_eda.uvm.interfaces.AsynchronousDataInterface(vulcan_eda.uvm.signals.Bundle(cocotb.top.upstream_first, cocotb.top.upstream_second)))
        self.downstream_agent = create_agent(self, "downstream_agent", vulcan_eda.uvm.interfaces.AsynchronousDataInterface(vulcan_eda.uvm.signals.Bundle(cocotb.top.downstream_first, cocotb.top.downstream_second, vulcan_eda.uvm.signals.Constant(0))), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class AsynchronousDataInterfaceTest(vulcan_eda.uvm.tests.BaseTest):
    drain_time_ns = 20
    timeout_us = 100

    def build_phase(self):
        self.env = AsynchronousDataInterfaceEnv("env", self)

    async def stimulus(self):
        data = AsynchronousDataInterfaceTest._one_change_per_step(100)
        for first, second in data:
            self.env.scoreboard.expected_data_analysis_fifo.analysis_export.write((first, second, 0))
        spaced_data_sequence = SpacedDataSequence.create("spaced_data_sequence")
        spaced_data_sequence.data_generator = data
        await spaced_data_sequence.start(self.env.upstream_agent.sequencer)

    @staticmethod
    def _one_change_per_step(count):
        values = iter(vulcan_eda.uvm.generators.RandomBitsGenerator(8))
        step = [0, 0]
        data = [tuple(step)]
        for index in range(count - 1):
            member = index % 2
            step[member] = next(value for value in values if value != step[member])
            data.append(tuple(step))
        return data

def test_asynchronous_data_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_asynchronous_data_interface",
        sources = [current_dir / "test_asynchronous_data_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_asynchronous_data_interface",
        hdl_toplevel = "test_asynchronous_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"]
    )
