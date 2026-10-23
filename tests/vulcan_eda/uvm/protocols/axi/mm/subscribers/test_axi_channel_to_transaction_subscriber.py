from vulcan_eda.uvm.protocols.axi.mm.data import AxiAddress, AxiReadData, AxiResponse, AxiTransaction, AxiWriteData, AxiWriteResponse
from vulcan_eda.uvm.protocols.axi.mm.subscribers import AxiChannelToTransactionSubscriber

def build(recording_subscriber):
    axi_channel_to_transaction_subscriber = AxiChannelToTransactionSubscriber.create("axi_channel_to_transaction_subscriber", None)
    axi_channel_to_transaction_subscriber.build_phase()
    axi_channel_to_transaction_subscriber.analysis_port.connect(recording_subscriber.analysis_export)
    return axi_channel_to_transaction_subscriber

def write(axi_channel_to_transaction_subscriber, channel, lower_item):
    axi_channel_to_transaction_subscriber.analysis_exports[channel].write(lower_item)

def test_publishes_nothing_before_write_response(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "aw", AxiAddress(address=0x10, bytes_per_beat=4))
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xAB, strobe=0xF))
    assert recording_subscriber.items == []

def test_publishes_write_at_write_response(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "aw", AxiAddress(address=0x10, bytes_per_beat=4, num_beats=2, id=3))
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xAB, strobe=0xF, last=False))
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xCD, strobe=0xF))
    write(axi_channel_to_transaction_subscriber, "b", AxiWriteResponse(response=AxiResponse.SLVERR, id=3))
    assert recording_subscriber.items == [AxiTransaction(
        access=AxiTransaction.Access.WRITE, address=0x10, data=(0xAB, 0xCD), num_beats=2, id=3, response=AxiResponse.SLVERR)]

def test_matches_write_data_arriving_before_address(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xAB, strobe=0xF))
    write(axi_channel_to_transaction_subscriber, "aw", AxiAddress(address=0x10, bytes_per_beat=4))
    write(axi_channel_to_transaction_subscriber, "b", AxiWriteResponse(response=AxiResponse.OKAY))
    assert recording_subscriber.items == [AxiTransaction(
        access=AxiTransaction.Access.WRITE, address=0x10, data=(0xAB,), response=AxiResponse.OKAY)]

def test_publishes_nothing_before_last_read_data(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "ar", AxiAddress(address=0x20, bytes_per_beat=4, num_beats=2))
    write(axi_channel_to_transaction_subscriber, "r", AxiReadData(data=0x12, response=AxiResponse.OKAY, last=False))
    assert recording_subscriber.items == []

def test_publishes_read_at_last_read_data(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "ar", AxiAddress(address=0x20, bytes_per_beat=4, num_beats=2, id=5))
    write(axi_channel_to_transaction_subscriber, "r", AxiReadData(data=0x12, response=AxiResponse.OKAY, last=False, id=5))
    write(axi_channel_to_transaction_subscriber, "r", AxiReadData(data=0x34, response=AxiResponse.DECERR, id=5))
    assert recording_subscriber.items == [AxiTransaction(
        access=AxiTransaction.Access.READ, address=0x20, data=(0x12, 0x34), num_beats=2, id=5, response=AxiResponse.DECERR)]

def test_matches_each_direction_in_order(recording_subscriber):
    axi_channel_to_transaction_subscriber = build(recording_subscriber)
    write(axi_channel_to_transaction_subscriber, "aw", AxiAddress(address=0x10, bytes_per_beat=4))
    write(axi_channel_to_transaction_subscriber, "ar", AxiAddress(address=0x20, bytes_per_beat=4))
    write(axi_channel_to_transaction_subscriber, "aw", AxiAddress(address=0x30, bytes_per_beat=4))
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xAB, strobe=0xF))
    write(axi_channel_to_transaction_subscriber, "r", AxiReadData(data=0x12, response=AxiResponse.OKAY))
    write(axi_channel_to_transaction_subscriber, "w", AxiWriteData(data=0xCD, strobe=0xF))
    write(axi_channel_to_transaction_subscriber, "b", AxiWriteResponse(response=AxiResponse.OKAY))
    write(axi_channel_to_transaction_subscriber, "b", AxiWriteResponse(response=AxiResponse.OKAY))
    assert recording_subscriber.items == [
        AxiTransaction(access=AxiTransaction.Access.READ, address=0x20, data=(0x12,), response=AxiResponse.OKAY),
        AxiTransaction(access=AxiTransaction.Access.WRITE, address=0x10, data=(0xAB,), response=AxiResponse.OKAY),
        AxiTransaction(access=AxiTransaction.Access.WRITE, address=0x30, data=(0xCD,), response=AxiResponse.OKAY)]
