import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm
import vulcan_eda.uvm.drivers.driver

class DataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        self.upstream_sequencer = pyuvm.uvm_sequencer.create("upstream_sequencer", self)
        upstream_interface = vulcan_eda.uvm.interfaces.DataInterface(cocotb.top.clk, cocotb.top.upstream_data)
        pyuvm.ConfigDB().set(self, "upstream_driver", "interface", upstream_interface)
        self.upstream_driver = vulcan_eda.uvm.drivers.driver.Driver.create("upstream_driver", self)

    def connect_phase(self):
        self.upstream_driver.seq_item_port.connect(self.upstream_sequencer.seq_item_export)

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
