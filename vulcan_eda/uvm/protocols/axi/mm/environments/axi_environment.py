import pyuvm

from vulcan_eda.uvm.agents.agent import Agent
from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig
from vulcan_eda.uvm.configs.layers.translation_layer_config import TranslationLayerConfig
from vulcan_eda.uvm.interfaces.ready_valid_data_receiver_interface import ReadyValidDataReceiverInterface
from vulcan_eda.uvm.interfaces.ready_valid_data_transmitter_interface import ReadyValidDataTransmitterInterface
from vulcan_eda.uvm.layers.translation_layer import TranslationLayer
from vulcan_eda.uvm.protocols.axi.mm.configs.axi_config import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.environments.axi_environment_config import AxiEnvironmentConfig
from vulcan_eda.uvm.protocols.axi.mm.data.axi_address import AxiAddress
from vulcan_eda.uvm.protocols.axi.mm.data.axi_read_data import AxiReadData
from vulcan_eda.uvm.protocols.axi.mm.data.axi_write_data import AxiWriteData
from vulcan_eda.uvm.protocols.axi.mm.data.axi_write_response import AxiWriteResponse
from vulcan_eda.uvm.protocols.axi.mm.sequences.axi_transaction_to_channel_sequence import AxiTransactionToChannelSequence
from vulcan_eda.uvm.protocols.axi.mm.subscribers.axi_channel_to_transaction_subscriber import AxiChannelToTransactionSubscriber
from vulcan_eda.uvm.signals.constant import Constant

class AxiEnvironment(pyuvm.uvm_env):
    def build_phase(self):
        self._config = AxiEnvironmentConfig.get(self)
        axi_config = AxiConfig.from_pins(self._config.profile, self._config.wdata, self._config.awaddr)
        self._agents = {}
        for channel, interface in self._interfaces(axi_config).items():
            AgentConfig(interface, self._config.is_active).set(self, f"{channel}_agent")
            self._agents[channel] = Agent.create(f"{channel}_agent", self)
        if self._config.is_active is pyuvm.uvm_active_passive_enum.UVM_ACTIVE:
            translation_sequence_type = AxiTransactionToChannelSequence
        else:
            translation_sequence_type = None
        TranslationLayerConfig(
            translation_sequence_type=translation_sequence_type,
            translation_subscriber_type=AxiChannelToTransactionSubscriber,
            forwarded_configs=(axi_config,)).set(self, "layer")
        self._layer = TranslationLayer.create("layer", self)
        self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def connect_phase(self):
        for channel, agent in self._agents.items():
            agent.analysis_port.connect(self._layer.analysis_exports[channel])
        self._layer.analysis_port.connect(self.analysis_port)
        if self._config.is_active is pyuvm.uvm_active_passive_enum.UVM_ACTIVE:
            for channel in AxiTransactionToChannelSequence.channels:
                self._layer.lower_sequencers[channel] = self._agents[channel].sequencer
            self.sequencer = self._layer.sequencer

    def _interfaces(self, axi_config):
        config = self._config
        size = Constant(axi_config.bytes_per_beat.bit_length() - 1)
        return {
            "aw": ReadyValidDataTransmitterInterface(config.clk, config.awready, config.awvalid, self._pins(
                address=config.awaddr, prot=config.awprot, bytes_per_beat=size if config.awsize is None else config.awsize,
                id=config.awid, num_beats=config.awlen, burst=config.awburst), AxiAddress),
            "w": ReadyValidDataTransmitterInterface(config.clk, config.wready, config.wvalid, self._pins(
                data=config.wdata, strobe=config.wstrb, last=config.wlast), AxiWriteData),
            "b": ReadyValidDataReceiverInterface(config.clk, config.bready, config.bvalid, self._pins(
                response=config.bresp, id=config.bid), AxiWriteResponse, idle_generator=config.bready_generator),
            "ar": ReadyValidDataTransmitterInterface(config.clk, config.arready, config.arvalid, self._pins(
                address=config.araddr, prot=config.arprot, bytes_per_beat=size if config.arsize is None else config.arsize,
                id=config.arid, num_beats=config.arlen, burst=config.arburst), AxiAddress),
            "r": ReadyValidDataReceiverInterface(config.clk, config.rready, config.rvalid, self._pins(
                data=config.rdata, response=config.rresp, id=config.rid, last=config.rlast), AxiReadData, idle_generator=config.rready_generator)}

    def _pins(self, **pins):
        return {name: pin for name, pin in pins.items() if pin is not None}
