import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

class ValidDataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(cocotb.top.clk, cocotb.top.upstream_valid, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_agent", "interface", upstream_interface)
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = vulcan_eda.uvm.interfaces.ValidDataInterface(cocotb.top.clk, cocotb.top.downstream_valid, cocotb.top.downstream_data)
        pyuvm.ConfigDB().set(self, "downstream_agent", "interface", downstream_interface)
        pyuvm.ConfigDB().set(self, "downstream_agent", "is_active", pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_agent.analysis_port.connect(self.scoreboard.expected_data_analysis_fifo.analysis_export)
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class ValidDataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = ValidDataInterfaceEnv("env", self)
        # self.random_valid_data_sequence = vulcan_eda.uvm.sequences.RandomValidDataSequence("random_valid_data_sequence")

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        # await self.random_data_sequence.start(self.env.upstream_agent.sequencer)
        self.drop_objection()

def test_valid_data_interface():
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path().absolute() / "tests" / "valid_data_interface"

    runner.build(
        hdl_toplevel = "test_valid_data_interface",
        sources = [current_dir / "test_valid_data_interface.vhdl"],
        build_dir = current_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_valid_data_interface",
        hdl_toplevel = "test_valid_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = current_dir,
        test_dir = current_dir,
        test_args = ["--std=08"]
    )
