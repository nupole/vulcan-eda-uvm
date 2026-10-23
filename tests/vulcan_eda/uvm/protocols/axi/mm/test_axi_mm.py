import pathlib

import cocotb
import cocotb.clock
import cocotb.triggers
import cocotb_tools.runner

import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.configs.agents import AgentConfig
from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.interfaces import ReadyValidDataReceiverInterface, ReadyValidDataTransmitterInterface
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.protocols.axi.mm.data import AxiAddress, AxiReadData, AxiResponse, AxiTransaction, AxiWriteData, AxiWriteResponse
from vulcan_eda.uvm.protocols.axi.mm.subscribers import AxiChannelToTransactionSubscriber
from vulcan_eda.uvm.sequences import IterableDataSequence, IterableValidDataSequence
from vulcan_eda.uvm.signals import Constant

DATA = (0x01234567, 0x89ABCDEF, 0xDEADBEEF, 0x0F0F0F0F)

class AxiMmEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        interfaces = {
            "aw": ReadyValidDataTransmitterInterface(dut.clk, dut.awready, dut.awvalid, {"address": dut.awaddr, "bytes_per_beat": Constant(2), "prot": dut.awprot}, AxiAddress),
            "w": ReadyValidDataTransmitterInterface(dut.clk, dut.wready, dut.wvalid, {"data": dut.wdata, "strobe": dut.wstrb}, AxiWriteData),
            "b": ReadyValidDataReceiverInterface(dut.clk, dut.bready, dut.bvalid, {"response": dut.bresp}, AxiWriteResponse),
            "ar": ReadyValidDataTransmitterInterface(dut.clk, dut.arready, dut.arvalid, {"address": dut.araddr, "bytes_per_beat": Constant(2), "prot": dut.arprot}, AxiAddress),
            "r": ReadyValidDataReceiverInterface(dut.clk, dut.rready, dut.rvalid, {"data": dut.rdata, "response": dut.rresp}, AxiReadData)}
        self.agents = {}
        for channel, interface in interfaces.items():
            pyuvm.ConfigDB().set(self, f"{channel}_agent", "config", AgentConfig(interface))
            self.agents[channel] = vulcan_eda.uvm.agents.Agent.create(f"{channel}_agent", self)
        pyuvm.ConfigDB().set(self, "layer", "config", TranslationLayerConfig(translation_subscriber_type=AxiChannelToTransactionSubscriber))
        self.layer = TranslationLayer.create("layer", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        for channel, agent in self.agents.items():
            agent.analysis_port.connect(self.layer.analysis_exports[channel])
        self.layer.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class AxiMmTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = AxiMmEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        await self._send(IterableDataSequence, "b", 1)
        await self._send(IterableDataSequence, "r", 1)
        for index, data in enumerate(DATA):
            await self._write(4 * index, data)
        for index, data in enumerate(DATA):
            await self._read(4 * index, data)
        await cocotb.triggers.ClockCycles(cocotb.top.clk, 5)
        self.drop_objection()

    async def _write(self, address, data):
        self._expect(AxiTransaction(access=AxiTransaction.Access.WRITE, address=address, data=(data,), response=AxiResponse.OKAY))
        address_task = cocotb.start_soon(self._send(IterableValidDataSequence, "aw", AxiAddress(address, 4)))
        await self._send(IterableValidDataSequence, "w", AxiWriteData(data, 0xF))
        await address_task

    async def _read(self, address, data):
        self._expect(AxiTransaction(access=AxiTransaction.Access.READ, address=address, data=(data,), response=AxiResponse.OKAY))
        await self._send(IterableValidDataSequence, "ar", AxiAddress(address, 4))

    async def _send(self, sequence_type, channel, item):
        sequence = sequence_type.create(f"{channel}_sequence")
        sequence.iterable = (item,)
        await sequence.start(self.env.agents[channel].sequencer)

    def _expect(self, txn):
        self.env.scoreboard.expected_data_analysis_fifo.analysis_export.write(txn)

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
