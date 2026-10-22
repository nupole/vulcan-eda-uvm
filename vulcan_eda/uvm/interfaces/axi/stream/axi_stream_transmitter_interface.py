from vulcan_eda.uvm.interfaces.ready_valid_data_transmitter_interface import ReadyValidDataTransmitterInterface
from vulcan_eda.uvm.sequences.axi.stream.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.signals import Bundle

class AxiStreamTransmitterInterface(ReadyValidDataTransmitterInterface):
    def __init__(self, clk, tready, tvalid, tdata, tlast):
        super().__init__(clk, tready, tvalid, Bundle(tdata, tlast))

    def _to_values(self, data):
        return data.to_values()

    def _from_values(self, values):
        return AxiStreamBeat.from_values(values)
