import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm
import vulcan_eda.uvm.drivers.driver
import vulcan_eda.uvm.monitors.monitor

class DataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = vulcan_eda.uvm.interfaces.DataInterface(cocotb.top.clk, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_agent", "interface", upstream_interface)
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = vulcan_eda.uvm.interfaces.DataInterface(cocotb.top.clk, cocotb.top.downstream_data)
        pyuvm.ConfigDB().set(self, "downstream_agent", "interface", downstream_interface)
        pyuvm.ConfigDB().set(self, "downstream_agent", "is_active", pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)

@pyuvm.test()
class DataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = DataInterfaceEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, units = "ns").start())
        self.drop_objection()

def test_data_interface():
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path().absolute() / "tests" / "data_interface"

    runner.build(
        hdl_toplevel = "test_data_interface",
        sources = [current_dir / "test_data_interface.vhdl"],
        build_dir = current_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_data_interface",
        hdl_toplevel = "test_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = current_dir,
        test_dir = current_dir,
        test_args = ["--std=08"]
    )
