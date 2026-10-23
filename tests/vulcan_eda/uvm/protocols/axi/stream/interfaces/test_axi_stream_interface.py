import pathlib
import random

import cocotb
import cocotb.clock
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.interfaces import AxiStreamReceiverInterface, AxiStreamTransmitterInterface
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_beat_sequence import AxiStreamBeatSequence
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_packet import AxiStreamPacket

class AxiStreamInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        upstream_interface = AxiStreamTransmitterInterface(cocotb.top.clk, cocotb.top.upstream_tready, cocotb.top.upstream_tvalid, cocotb.top.upstream_tdata, cocotb.top.upstream_tlast)
        self.upstream_axi_stream_config = AxiStreamConfig.from_tdata(cocotb.top.upstream_tdata)
        pyuvm.ConfigDB().set(self, "upstream_agent.sequencer", "axi_stream_config", self.upstream_axi_stream_config)
        pyuvm.ConfigDB().set(self, "upstream_agent", "config", vulcan_eda.uvm.agents.AgentConfig(upstream_interface))
        self.upstream_agent = vulcan_eda.uvm.agents.Agent.create("upstream_agent", self)
        downstream_interface = AxiStreamReceiverInterface(cocotb.top.clk, cocotb.top.downstream_tready, cocotb.top.downstream_tvalid, cocotb.top.downstream_tdata, cocotb.top.downstream_tlast)
        pyuvm.ConfigDB().set(self, "downstream_agent", "config", vulcan_eda.uvm.agents.AgentConfig(downstream_interface))
        self.downstream_agent = vulcan_eda.uvm.agents.Agent.create("downstream_agent", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.upstream_agent.analysis_port.connect(self.scoreboard.expected_data_analysis_fifo.analysis_export)
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class AxiStreamInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = AxiStreamInterfaceEnv("env", self)
        pyuvm.ConfigDB().set(self, "env.upstream_agent.sequencer", "transaction_sequence_config", vulcan_eda.uvm.sequences.TransactionSequenceConfig(txn_pct=50))
        pyuvm.ConfigDB().set(self, "env.downstream_agent.sequencer", "random_data_sequence_config", vulcan_eda.uvm.sequences.RandomDataSequenceConfig(max_data=1))

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        cocotb.start_soon(self._drive_ready())
        for _ in range(4):
            packet = AxiStreamPacket(random.randbytes(self.env.upstream_axi_stream_config.num_bytes * random.randint(1, 16)))
            axi_stream_beat_sequence = AxiStreamBeatSequence("axi_stream_beat_sequence", packet.to_beats(self.env.upstream_axi_stream_config.num_bytes))
            await axi_stream_beat_sequence.start(self.env.upstream_agent.sequencer)
        self.drop_objection()

    async def _drive_ready(self):
        while True:
            random_data_sequence = vulcan_eda.uvm.sequences.RandomDataSequence("random_data_sequence")
            await random_data_sequence.start(self.env.downstream_agent.sequencer)

def test_axi_stream_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_axi_stream_interface",
        sources = [current_dir / "test_axi_stream_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_axi_stream_interface",
        hdl_toplevel = "test_axi_stream_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
