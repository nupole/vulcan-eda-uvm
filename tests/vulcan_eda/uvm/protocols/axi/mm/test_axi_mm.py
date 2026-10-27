import dataclasses
import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.generators import RandomBooleanGenerator
from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.environments import AxiEnvironmentConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.sequences import AxiTransactionSequenceConfig, AxiTransactionToChannelSequenceConfig
from vulcan_eda.uvm.protocols.axi.mm.data import AxiResponse, AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.environments import AxiEnvironment
from vulcan_eda.uvm.protocols.axi.mm.sequences import RandomAxiTransactionSequence

from tests.support.components import RecordingSubscriber, create_agent

class RecordingRandomAxiTransactionSequence(RandomAxiTransactionSequence):
    def configure(self):
        super().configure()
        self._registers = {}

    def get_next_txn(self):
        txn = super().get_next_txn()
        if txn.access is AxiTransaction.Access.WRITE:
            self._registers[txn.address] = txn.data[0]
            expected_txn = dataclasses.replace(txn, response=AxiResponse.OKAY)
        else:
            expected_txn = dataclasses.replace(txn, data=(self._registers.get(txn.address, 0),), response=AxiResponse.OKAY)
        for expected_analysis_export in self.expected_analysis_exports:
            expected_analysis_export.write(expected_txn)
        return txn

class AxiMmEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        AxiEnvironmentConfig.from_prefix(
            dut, "", clk=dut.clk, profile=AxiConfig.Profile.LITE,
            bready_generator=RandomBooleanGenerator(50), rready_generator=RandomBooleanGenerator(50)).set(self, "axi_environment")
        self.axi_environment = AxiEnvironment.create("axi_environment", self)
        AxiEnvironmentConfig.from_prefix(
            dut, "", clk=dut.clk, profile=AxiConfig.Profile.LITE, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE).set(self, "passive_axi_environment")
        self.passive_axi_environment = AxiEnvironment.create("passive_axi_environment", self)
        self.ready_agent = create_agent(self, "ready_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, vulcan_eda.uvm.signals.Bundle(dut.bready, dut.rready)), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.ready_recorder = RecordingSubscriber.create("ready_recorder", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)
        self.passive_scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("passive_scoreboard", self)

    def connect_phase(self):
        self.axi_environment.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)
        self.passive_axi_environment.analysis_port.connect(self.passive_scoreboard.actual_data_analysis_fifo.analysis_export)
        self.ready_agent.analysis_port.connect(self.ready_recorder.analysis_export)

@pyuvm.test()
class AxiMmTest(vulcan_eda.uvm.tests.BaseTest):
    timeout_us = 100

    def build_phase(self):
        self.env = AxiMmEnv("env", self)

    async def stimulus(self):
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        recording_random_axi_transaction_sequence = RecordingRandomAxiTransactionSequence.create("recording_random_axi_transaction_sequence")
        recording_random_axi_transaction_sequence.expected_analysis_exports = [
            scoreboard.expected_data_analysis_fifo.analysis_export for scoreboard in (self.env.scoreboard, self.env.passive_scoreboard)]
        AxiTransactionSequenceConfig(num_txn=200).set(self.env.axi_environment.sequencer)
        AxiTransactionToChannelSequenceConfig(
            awvalid_generator=RandomBooleanGenerator(50), wvalid_generator=RandomBooleanGenerator(50),
            arvalid_generator=RandomBooleanGenerator(50)).set(self.env.axi_environment.sequencer)
        await recording_random_axi_transaction_sequence.start(self.env.axi_environment.sequencer)

    def check_phase(self):
        for channel, readies in zip(("b", "r"), zip(*self.env.ready_recorder.items)):
            if all(ready == 1 for ready in readies):
                self.uvm_report.error("NO_BACKPRESSURE", f"the manager never lowered {channel}ready")

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
