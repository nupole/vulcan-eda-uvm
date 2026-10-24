import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

class Handle:
    def __init__(self, width):
        self.width = width
        self.value = 0

    def __len__(self):
        return self.width

def test_reads_and_drives_a_raw_pin():
    handle = Handle(8)
    data_interface = vulcan_eda.uvm.interfaces.DataInterface(None, handle)
    data_interface.write_data(3)
    assert (handle.value, data_interface.read_data()) == (3, 3)

def test_idle_holds_the_pin_by_default():
    handle = Handle(8)
    data_interface = vulcan_eda.uvm.interfaces.DataInterface(None, handle)
    data_interface.write_data(3)
    data_interface.write_idle()
    assert handle.value == 3

def test_idle_drives_its_idle_generator():
    handle = Handle(8)
    data_interface = vulcan_eda.uvm.interfaces.DataInterface(None, handle, vulcan_eda.uvm.generators.IterableGenerator((4, 5)))
    data_interface.write_idle()
    first = handle.value
    data_interface.write_idle()
    assert (first, handle.value) == (4, 5)

def test_keeps_signal_adapters():
    assert vulcan_eda.uvm.interfaces.DataInterface(None, vulcan_eda.uvm.signals.Constant(1)).read_data() == 1

class DataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = vulcan_eda.uvm.interfaces.DataInterface(cocotb.top.clk, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_agent", "config", vulcan_eda.uvm.configs.agents.AgentConfig(upstream_interface))
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = vulcan_eda.uvm.interfaces.DataInterface(cocotb.top.clk, cocotb.top.downstream_data)
        pyuvm.ConfigDB().set(self, "downstream_agent", "config", vulcan_eda.uvm.configs.agents.AgentConfig(downstream_interface, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE))
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_agent.analysis_port.connect(self.scoreboard.expected_data_analysis_fifo.analysis_export)
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class DataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = DataInterfaceEnv("env", self)
        self.random_data_sequence = vulcan_eda.uvm.sequences.RandomDataSequence("random_data_sequence")

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        await self.random_data_sequence.start(self.env.upstream_agent.sequencer)
        self.drop_objection()

def test_data_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_data_interface",
        sources = [current_dir / "test_data_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_data_interface",
        hdl_toplevel = "test_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"]
    )
