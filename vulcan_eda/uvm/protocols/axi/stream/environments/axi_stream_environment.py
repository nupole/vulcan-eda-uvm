import pyuvm

from vulcan_eda.uvm.agents.agent import Agent
from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig
from vulcan_eda.uvm.configs.layers.translation_layer_config import TranslationLayerConfig
from vulcan_eda.uvm.interfaces.ready_valid_data_receiver_interface import ReadyValidDataReceiverInterface
from vulcan_eda.uvm.interfaces.ready_valid_data_transmitter_interface import ReadyValidDataTransmitterInterface
from vulcan_eda.uvm.layers.translation_layer import TranslationLayer
from vulcan_eda.uvm.protocols.axi.stream.configs.axi_stream_config import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.environments.axi_stream_environment_config import AxiStreamEnvironmentConfig
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_packet_to_beat_sequence import AxiStreamPacketToBeatSequence
from vulcan_eda.uvm.protocols.axi.stream.subscribers.axi_stream_beat_to_packet_subscriber import AxiStreamBeatToPacketSubscriber

class AxiStreamEnvironment(pyuvm.uvm_env):
    def build_phase(self):
        self._config = AxiStreamEnvironmentConfig.get(self)
        AgentConfig(self._interface(), self._config.is_active).set(self, "agent")
        self._agent = Agent.create("agent", self)
        if self._is_active_transmitter():
            translation_sequence_type = AxiStreamPacketToBeatSequence
        else:
            translation_sequence_type = None
        TranslationLayerConfig(
            translation_sequence_type=translation_sequence_type,
            translation_subscriber_type=AxiStreamBeatToPacketSubscriber,
            forwarded_configs=(AxiStreamConfig.from_tdata(self._config.tdata),)).set(self, "layer")
        self._layer = TranslationLayer.create("layer", self)
        self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def connect_phase(self):
        self._agent.analysis_port.connect(self._layer.analysis_exports["stream"])
        self._layer.analysis_port.connect(self.analysis_port)
        if self._is_active_transmitter():
            self._layer.lower_sequencers["stream"] = self._agent.sequencer
            self.sequencer = self._layer.sequencer

    def _interface(self):
        config = self._config
        pins = {"data": config.tdata, "last": config.tlast}
        if config.role is AxiStreamEnvironmentConfig.Role.TRANSMITTER:
            return ReadyValidDataTransmitterInterface(config.clk, config.tready, config.tvalid, pins, AxiStreamBeat)
        return ReadyValidDataReceiverInterface(config.clk, config.tready, config.tvalid, pins, AxiStreamBeat, idle_generator=config.ready_generator)

    def _is_active_transmitter(self):
        return self._config.role is AxiStreamEnvironmentConfig.Role.TRANSMITTER and self._config.is_active is pyuvm.uvm_active_passive_enum.UVM_ACTIVE
