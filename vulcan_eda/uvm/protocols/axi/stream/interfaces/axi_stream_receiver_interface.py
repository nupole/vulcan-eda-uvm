from vulcan_eda.uvm.interfaces.ready_valid_data_receiver_interface import ReadyValidDataReceiverInterface
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.signals import Bundle

class AxiStreamReceiverInterface(ReadyValidDataReceiverInterface):
    def __init__(self, clk, tready, tvalid, tdata, tlast):
        super().__init__(clk, tready, tvalid, Bundle(tdata, tlast))

    def _from_values(self, values):
        return AxiStreamBeat.from_values(values)
