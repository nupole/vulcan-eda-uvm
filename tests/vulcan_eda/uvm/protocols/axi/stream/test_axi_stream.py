import pathlib

import cocotb
import cocotb.clock
import cocotb.triggers
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.configs.agents import AgentConfig
from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.generators import RandomBooleanGenerator
from vulcan_eda.uvm.interfaces import ReadyValidDataReceiverInterface, ReadyValidDataTransmitterInterface
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketSequenceConfig, AxiStreamPacketToBeatSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.data import AxiStreamBeat
from vulcan_eda.uvm.protocols.axi.stream.sequences import AxiStreamPacketToBeatSequence, RandomAxiStreamPacketSequence
from vulcan_eda.uvm.protocols.axi.stream.subscribers import AxiStreamBeatToPacketSubscriber
from vulcan_eda.uvm.sequences import DataSequence

class RecordingRandomAxiStreamPacketSequence(RandomAxiStreamPacketSequence):
    def _get_next_packet(self):
        packet = super()._get_next_packet()
        self.expected_analysis_export.write(packet)
        return packet

class TransferRecorder(pyuvm.uvm_subscriber):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.transfers = []

    def write(self, ready_valid_last):
        ready, valid, last = ready_valid_last
        self.transfers.append((ready == 1 and valid == 1, last == 1))

class AxiStreamEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        upstream_interface = ReadyValidDataTransmitterInterface(dut.clk, dut.upstream_tready, dut.upstream_tvalid, {"data": dut.upstream_tdata, "last": dut.upstream_tlast}, AxiStreamBeat)
        AgentConfig(upstream_interface).set(self, "upstream_agent")
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        TranslationLayerConfig(
            translation_sequence_type=AxiStreamPacketToBeatSequence,
            forwarded_configs=(AxiStreamConfig.from_tdata(dut.upstream_tdata),)).set(self, "upstream_layer")
        self.upstream_layer = TranslationLayer.create("upstream_layer", self)
        downstream_interface = ReadyValidDataReceiverInterface(dut.clk, dut.downstream_tready, dut.downstream_tvalid, {"data": dut.downstream_tdata, "last": dut.downstream_tlast}, AxiStreamBeat)
        AgentConfig(downstream_interface).set(self, "downstream_agent")
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        TranslationLayerConfig(
            translation_subscriber_type=AxiStreamBeatToPacketSubscriber,
            forwarded_configs=(AxiStreamConfig.from_tdata(dut.downstream_tdata),)).set(self, "downstream_layer")
        self.downstream_layer = TranslationLayer.create("downstream_layer", self)
        transfer_interface = vulcan_eda.uvm.interfaces.DataInterface(dut.clk, vulcan_eda.uvm.signals.Bundle(dut.downstream_tready, dut.downstream_tvalid, dut.downstream_tlast))
        AgentConfig(transfer_interface, pyuvm.uvm_active_passive_enum.UVM_PASSIVE).set(self, "transfer_agent")
        self.transfer_agent = vulcan_eda.uvm.agents.Agent.create("transfer_agent", self)
        self.transfer_recorder = TransferRecorder.create("transfer_recorder", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_layer.lower_sequencers["stream"] = self.upstream_agent.sequencer
        self.downstream_agent.analysis_port.connect(self.downstream_layer.analysis_exports["stream"])
        self.downstream_layer.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)
        self.transfer_agent.analysis_port.connect(self.transfer_recorder.analysis_export)

@pyuvm.test()
class AxiStreamTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = AxiStreamEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        ready_sequence = DataSequence.create("ready_sequence")
        ready_sequence.data_generator = RandomBooleanGenerator(50)
        cocotb.start_soon(ready_sequence.start(self.env.downstream_agent.sequencer))
        AxiStreamPacketToBeatSequenceConfig(RandomBooleanGenerator(50)).set(self.env.upstream_layer.sequencer)
        AxiStreamPacketSequenceConfig(num_packets=100).set(self.env.upstream_layer.sequencer)
        recording_random_axi_stream_packet_sequence = RecordingRandomAxiStreamPacketSequence.create("recording_random_axi_stream_packet_sequence")
        recording_random_axi_stream_packet_sequence.expected_analysis_export = self.env.scoreboard.expected_data_analysis_fifo.analysis_export
        await recording_random_axi_stream_packet_sequence.start(self.env.upstream_layer.sequencer)
        await cocotb.triggers.ClockCycles(cocotb.top.clk, 2)
        transfers = self.env.transfer_recorder.transfers
        assert any(last_transfer and last and next_transfer for (last_transfer, last), (next_transfer, _) in zip(transfers, transfers[1:]))
        self.drop_objection()

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
