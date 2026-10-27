import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.generators import RandomBooleanGenerator
from vulcan_eda.uvm.protocols.axi.stream.configs.environments import AxiStreamEnvironmentConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketSequenceConfig, AxiStreamPacketToBeatSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.environments import AxiStreamEnvironment
from vulcan_eda.uvm.protocols.axi.stream.sequences import RandomAxiStreamPacketSequence

from tests.support.components import RecordingSubscriber, create_agent

class RecordingRandomAxiStreamPacketSequence(RandomAxiStreamPacketSequence):
    def get_next_packet(self):
        packet = super().get_next_packet()
        for expected_analysis_export in self.expected_analysis_exports:
            expected_analysis_export.write(packet)
        return packet

class AxiStreamEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        AxiStreamEnvironmentConfig.from_prefix(dut, "upstream_", clk=dut.clk, role=AxiStreamEnvironmentConfig.Role.TRANSMITTER).set(self, "upstream_environment")
        self.upstream_environment = AxiStreamEnvironment.create("upstream_environment", self)
        AxiStreamEnvironmentConfig.from_prefix(dut, "downstream_", clk=dut.clk, role=AxiStreamEnvironmentConfig.Role.RECEIVER, ready_generator=RandomBooleanGenerator(50)).set(self, "downstream_environment")
        self.downstream_environment = AxiStreamEnvironment.create("downstream_environment", self)
        AxiStreamEnvironmentConfig.from_prefix(dut, "downstream_", clk=dut.clk, role=AxiStreamEnvironmentConfig.Role.RECEIVER, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE).set(self, "passive_environment")
        self.passive_environment = AxiStreamEnvironment.create("passive_environment", self)
        transfer_interface = vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, vulcan_eda.uvm.signals.Bundle(dut.downstream_tready, dut.downstream_tvalid, dut.downstream_tlast))
        self.transfer_agent = create_agent(self, "transfer_agent", transfer_interface, pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.transfer_recorder = RecordingSubscriber.create("transfer_recorder", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)
        self.passive_scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("passive_scoreboard", self)

    def connect_phase(self):
        self.downstream_environment.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)
        self.passive_environment.analysis_port.connect(self.passive_scoreboard.actual_data_analysis_fifo.analysis_export)
        self.transfer_agent.analysis_port.connect(self.transfer_recorder.analysis_export)

@pyuvm.test()
class AxiStreamTest(vulcan_eda.uvm.tests.BaseTest):
    drain_time_ns = 20
    timeout_us = 100

    def build_phase(self):
        self.env = AxiStreamEnv("env", self)

    async def stimulus(self):
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        AxiStreamPacketToBeatSequenceConfig(RandomBooleanGenerator(50)).set(self.env.upstream_environment.sequencer)
        AxiStreamPacketSequenceConfig(num_packets=100).set(self.env.upstream_environment.sequencer)
        recording_random_axi_stream_packet_sequence = RecordingRandomAxiStreamPacketSequence.create("recording_random_axi_stream_packet_sequence")
        recording_random_axi_stream_packet_sequence.expected_analysis_exports = [
            scoreboard.expected_data_analysis_fifo.analysis_export for scoreboard in (self.env.scoreboard, self.env.passive_scoreboard)]
        await recording_random_axi_stream_packet_sequence.start(self.env.upstream_environment.sequencer)

    def check_phase(self):
        transfers = [(ready == 1 and valid == 1, last == 1) for ready, valid, last in self.env.transfer_recorder.items]
        if not any(last_transfer and last and next_transfer for (last_transfer, last), (next_transfer, _) in zip(transfers, transfers[1:])):
            self.uvm_report.error("BACK_TO_BACK", "no packet started right after the previous one ended")
        if all(ready == 1 for ready, _, _ in self.env.transfer_recorder.items):
            self.uvm_report.error("NO_BACKPRESSURE", "the receiver never lowered tready")

def test_axi_stream(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_axi_stream",
        sources = [current_dir / "test_axi_stream.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_axi_stream",
        hdl_toplevel = "test_axi_stream",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
