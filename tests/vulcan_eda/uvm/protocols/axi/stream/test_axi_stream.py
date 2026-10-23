import pathlib

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.configs.agents import AgentConfig
from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.configs.sequences import RandomDataSequenceConfig, TransactionSequenceConfig
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.interfaces import AxiStreamReceiverInterface, AxiStreamTransmitterInterface
from vulcan_eda.uvm.protocols.axi.stream.sequences import AxiStreamPacketToBeatSequence, RandomAxiStreamPacketSequence
from vulcan_eda.uvm.protocols.axi.stream.subscribers import AxiStreamBeatToPacketSubscriber

class RecordingRandomAxiStreamPacketSequence(RandomAxiStreamPacketSequence):
    def _get_next_packet(self):
        packet = super()._get_next_packet()
        self.expected_analysis_export.write(packet)
        return packet

class AxiStreamEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        upstream_interface = AxiStreamTransmitterInterface(dut.clk, dut.upstream_tready, dut.upstream_tvalid, dut.upstream_tdata, dut.upstream_tlast)
        pyuvm.ConfigDB().set(self, "upstream_agent", "config", AgentConfig(upstream_interface))
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        pyuvm.ConfigDB().set(self, "upstream_layer", "config", TranslationLayerConfig(
            translation_sequence_type=AxiStreamPacketToBeatSequence,
            forwarded_configs={"axi_stream_config": AxiStreamConfig.from_tdata(dut.upstream_tdata)}))
        self.upstream_layer = TranslationLayer.create("upstream_layer", self)
        downstream_interface = AxiStreamReceiverInterface(dut.clk, dut.downstream_tready, dut.downstream_tvalid, dut.downstream_tdata, dut.downstream_tlast)
        pyuvm.ConfigDB().set(self, "downstream_agent", "config", AgentConfig(downstream_interface))
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        pyuvm.ConfigDB().set(self, "downstream_layer", "config", TranslationLayerConfig(
            translation_subscriber_type=AxiStreamBeatToPacketSubscriber,
            forwarded_configs={"axi_stream_config": AxiStreamConfig.from_tdata(dut.downstream_tdata)}))
        self.downstream_layer = TranslationLayer.create("downstream_layer", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_layer.lower_sequencer = self.upstream_agent.sequencer
        self.downstream_agent.analysis_port.connect(self.downstream_layer.analysis_export)
        self.downstream_layer.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class AxiStreamTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = AxiStreamEnv("env", self)
        pyuvm.ConfigDB().set(self, "env.upstream_agent.sequencer", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
        pyuvm.ConfigDB().set(self, "env.downstream_agent.sequencer", "random_data_sequence_config", RandomDataSequenceConfig(max_data=1))

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        cocotb.start_soon(self._drive_ready())
        recording_random_axi_stream_packet_sequence = RecordingRandomAxiStreamPacketSequence.create("recording_random_axi_stream_packet_sequence")
        recording_random_axi_stream_packet_sequence.expected_analysis_export = self.env.scoreboard.expected_data_analysis_fifo.analysis_export
        await recording_random_axi_stream_packet_sequence.start(self.env.upstream_layer.sequencer)
        self.drop_objection()

    async def _drive_ready(self):
        while True:
            random_data_sequence = vulcan_eda.uvm.sequences.RandomDataSequence("random_data_sequence")
            await random_data_sequence.start(self.env.downstream_agent.sequencer)

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
