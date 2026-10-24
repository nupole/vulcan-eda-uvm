import itertools
import pathlib

import cocotb
import cocotb.clock
import cocotb.triggers
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

class Handle:
    def __init__(self, width):
        self.width = width
        self.value = 0

    def __len__(self):
        return self.width

def test_idle_drives_valid_low_and_random_data_by_default():
    valid, data = Handle(1), Handle(16)
    valid_data_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(None, valid, vulcan_eda.uvm.signals.Bundle(data, vulcan_eda.uvm.signals.Constant(0)))
    driven = set()
    for _ in range(50):
        valid_data_interface.write_idle()
        driven.add(data.value)
    assert valid.value == 0
    assert len(driven) > 1

def test_idle_drives_its_idle_generator():
    valid, data = Handle(1), Handle(16)
    valid_data_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(None, valid, data, vulcan_eda.uvm.generators.ConstantGenerator(7))
    valid_data_interface.write_idle()
    assert (valid.value, data.value) == (0, 7)

def test_data_is_driven_with_valid_high():
    valid, data = Handle(1), Handle(16)
    vulcan_eda.uvm.interfaces.ValidDataInterface(None, valid, data).write_valid_data(1, 3)
    assert (valid.value, data.value) == (1, 3)

class ValidDataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(cocotb.top.clk, cocotb.top.upstream_valid, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_agent", "config", vulcan_eda.uvm.configs.agents.AgentConfig(upstream_interface))
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(cocotb.top.clk, cocotb.top.downstream_valid, cocotb.top.downstream_data)
        pyuvm.ConfigDB().set(self, "downstream_agent", "config", vulcan_eda.uvm.configs.agents.AgentConfig(downstream_interface, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE))
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class ValidDataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = ValidDataInterfaceEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        valid_data_sequence = vulcan_eda.uvm.sequences.ValidDataSequence.create("valid_data_sequence")
        valid_data_sequence.valid_generator = vulcan_eda.uvm.generators.RandomBooleanGenerator(50)
        data = list(itertools.islice(vulcan_eda.uvm.generators.RandomBitsGenerator(8), 100))
        for value in data:
            self.env.scoreboard.expected_data_analysis_fifo.analysis_export.write(value)
        valid_data_sequence.data_generator = data
        await valid_data_sequence.start(self.env.upstream_agent.sequencer)
        await cocotb.triggers.ClockCycles(cocotb.top.clk, 2)
        self.drop_objection()

def test_valid_data_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_valid_data_interface",
        sources = [current_dir / "test_valid_data_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_valid_data_interface",
        hdl_toplevel = "test_valid_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
