import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

class ReadyValidDataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = vulcan_eda.uvm.interfaces.ReadyValidDataInterface(cocotb.top.clk, cocotb.top.upstream_ready, cocotb.top.upstream_valid, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_agent", "interface", upstream_interface)
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = vulcan_eda.uvm.interfaces.ReadyValidDataInterface(cocotb.top.clk, cocotb.top.downstream_ready, cocotb.top.downstream_valid, cocotb.top.downstream_data)
        pyuvm.ConfigDB().set(self, "downstream_agent", "interface", downstream_interface)
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_agent.analysis_port.connect(self.scoreboard.expected_data_analysis_fifo.analysis_export)
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class ReadyValidDataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = ReadyValidDataInterfaceEnv("env", self)
        pyuvm.ConfigDB().set(self, "env.upstream_agent.sequencer", "txn_pct", 50)
        pyuvm.ConfigDB().set(self, "env.downstream_agent.sequencer", "txn_pct", 50)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        self.drop_objection()

def test_ready_valid_data_interface():
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path().absolute() / "tests" / "ready_valid_data_interface"

    runner.build(
        hdl_toplevel = "test_ready_valid_data_interface",
        sources = [current_dir / "test_ready_valid_data_interface.vhdl"],
        build_dir = current_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_ready_valid_data_interface",
        hdl_toplevel = "test_ready_valid_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = current_dir,
        test_dir = current_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
