import itertools
import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from tests.support.components import RecordingSubscriber, create_agent
from tests.support.signals import Handle

def test_reads_and_drives_a_raw_pin():
    handle = Handle(8)
    synchronous_data_interface = vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, handle)
    synchronous_data_interface.write_data(3)
    assert (handle.value, synchronous_data_interface.read_data()) == (3, 3)

def test_idle_holds_the_pin_by_default():
    handle = Handle(8)
    synchronous_data_interface = vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, handle)
    synchronous_data_interface.write_data(3)
    synchronous_data_interface.write_idle()
    assert handle.value == 3

def test_idle_drives_its_idle_generator():
    handle = Handle(8)
    synchronous_data_interface = vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, handle, vulcan_eda.uvm.generators.IterableGenerator((4, 5)))
    synchronous_data_interface.write_idle()
    first = handle.value
    synchronous_data_interface.write_idle()
    assert (first, handle.value) == (4, 5)

def test_keeps_signal_adapters():
    assert vulcan_eda.uvm.interfaces.SynchronousDataInterface(None, vulcan_eda.uvm.signals.Constant(1)).read_data() == 1

class DataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        self.upstream_agent = create_agent(self, "upstream_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(cocotb.top.clk, cocotb.top.upstream_data))
        self.downstream_agent = create_agent(self, "downstream_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(cocotb.top.clk, cocotb.top.downstream_data), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.data_recorder = RecordingSubscriber.create("data_recorder", self)

    def connect_phase(self):
        self.downstream_agent.analysis_port.connect(self.data_recorder.analysis_export)

@pyuvm.test()
class DataInterfaceTest(vulcan_eda.uvm.tests.BaseTest):
    drain_time_ns = 20
    timeout_us = 100

    def build_phase(self):
        self.env = DataInterfaceEnv("env", self)

    async def stimulus(self):
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        data_sequence = vulcan_eda.uvm.sequences.DataSequence.create("data_sequence")
        self.data = list(itertools.islice(vulcan_eda.uvm.generators.RandomBitsGenerator(8), 100))
        data_sequence.data_generator = self.data
        await data_sequence.start(self.env.upstream_agent.sequencer)

    def check_phase(self):
        recorded = self.env.data_recorder.items
        if not any(recorded[start:start + len(self.data)] == self.data for start in range(len(recorded))):
            self.uvm_report.error("NOT_RECORDED", "the driven data never appeared contiguously on the outputs")

def test_synchronous_data_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_synchronous_data_interface",
        sources = [current_dir / "test_synchronous_data_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_synchronous_data_interface",
        hdl_toplevel = "test_synchronous_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"]
    )
