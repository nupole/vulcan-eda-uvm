import asyncio

import pytest

from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.data import AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.sequences import AxiTransactionToChannelSequence
from vulcan_eda.uvm.sequences import DataSequenceItem

def test_rejects_a_burst_on_axi_lite_before_driving_anything(upper_sequencer):
    AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=4, address_width=8).set(upper_sequencer)
    axi_transaction_to_channel_sequence = AxiTransactionToChannelSequence.create("axi_transaction_to_channel_sequence")
    axi_transaction_to_channel_sequence.upper_sequencer = upper_sequencer
    burst = AxiTransaction(access=AxiTransaction.Access.WRITE, address=0, data=(1, 2), num_beats=2)
    with pytest.raises(ValueError, match="single beat"):
        asyncio.run(axi_transaction_to_channel_sequence.translate(DataSequenceItem("request", burst)))
