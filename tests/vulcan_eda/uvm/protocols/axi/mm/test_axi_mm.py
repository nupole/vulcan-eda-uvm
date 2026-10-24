import dataclasses
import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.environments import AxiEnvironmentConfig
from vulcan_eda.uvm.protocols.axi.mm.data import AxiResponse, AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.environments import AxiEnvironment
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem

DATA = (0x01234567, 0x89ABCDEF, 0xDEADBEEF, 0x0F0F0F0F)

class AxiTransactionSequence(pyuvm.uvm_sequence):
    txns = ()

    async def body(self):
        for txn in self.txns:
            sequence_item = DataSequenceItem("axi_transaction_sequence_item", txn)
            await self.start_item(sequence_item)
            await self.finish_item(sequence_item)
            await self.get_response()

class AxiMmEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        pyuvm.ConfigDB().set(self, "axi_environment", "config", AxiEnvironmentConfig.from_prefix(
            dut, "", clk=dut.clk, profile=AxiConfig.Profile.LITE))
        self.axi_environment = AxiEnvironment.create("axi_environment", self)
        pyuvm.ConfigDB().set(self, "passive_axi_environment", "config", AxiEnvironmentConfig.from_prefix(
            dut, "", clk=dut.clk, profile=AxiConfig.Profile.LITE, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE))
        self.passive_axi_environment = AxiEnvironment.create("passive_axi_environment", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)
        self.passive_scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("passive_scoreboard", self)

    def connect_phase(self):
        self.axi_environment.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)
        self.passive_axi_environment.analysis_port.connect(self.passive_scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class AxiMmTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = AxiMmEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        writes = [AxiTransaction(access=AxiTransaction.Access.WRITE, address=4 * index, data=(data,)) for index, data in enumerate(DATA)]
        reads = [AxiTransaction(access=AxiTransaction.Access.READ, address=4 * index) for index in range(len(DATA))]
        for write in writes:
            self._expect(dataclasses.replace(write, response=AxiResponse.OKAY))
        for read, data in zip(reads, DATA):
            self._expect(dataclasses.replace(read, data=(data,), response=AxiResponse.OKAY))
        axi_transaction_sequence = AxiTransactionSequence.create("axi_transaction_sequence")
        axi_transaction_sequence.txns = writes + reads
        await axi_transaction_sequence.start(self.env.axi_environment.sequencer)
        self.drop_objection()

    def _expect(self, txn):
        for scoreboard in (self.env.scoreboard, self.env.passive_scoreboard):
            scoreboard.expected_data_analysis_fifo.analysis_export.write(txn)

def test_axi_mm(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_axi_mm",
        sources = [current_dir / "test_axi_mm.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_axi_mm",
        hdl_toplevel = "test_axi_mm",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
