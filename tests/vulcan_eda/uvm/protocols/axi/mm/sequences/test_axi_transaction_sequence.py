import pytest
import pyuvm

from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.sequences import AxiTransactionSequenceConfig
from vulcan_eda.uvm.protocols.axi.mm.data import AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.sequences import AxiTransactionSequence, RandomAxiTransactionSequence

def txns(axi_transaction_sequence_config=None, address_width=8):
    pyuvm.ConfigDB().set(None, "", "axi_config", AxiConfig(AxiConfig.Profile.LITE, bytes_per_beat=4, address_width=address_width))
    if axi_transaction_sequence_config is not None:
        pyuvm.ConfigDB().set(None, "", "axi_transaction_sequence_config", axi_transaction_sequence_config)
    random_axi_transaction_sequence = RandomAxiTransactionSequence.create("random_axi_transaction_sequence")
    random_axi_transaction_sequence._configure()
    return [random_axi_transaction_sequence._get_next_txn() for _ in range(200)]

def test_addresses_are_aligned_and_in_range():
    addresses = {txn.address for txn in txns(AxiTransactionSequenceConfig(min_address=5, max_address=19))}
    assert addresses == {8, 12, 16}

def test_max_address_defaults_to_address_width():
    assert {txn.address for txn in txns(address_width=4)} == {0, 4, 8, 12}

def test_write_pct_100_sends_only_writes():
    assert {txn.access for txn in txns(AxiTransactionSequenceConfig(write_pct=100))} == {AxiTransaction.Access.WRITE}

def test_write_pct_0_sends_only_reads():
    assert {txn.access for txn in txns(AxiTransactionSequenceConfig(write_pct=0))} == {AxiTransaction.Access.READ}

def test_writes_carry_one_full_width_beat():
    writes = txns(AxiTransactionSequenceConfig(write_pct=100))
    assert all(len(txn.data) == 1 and 0 <= txn.data[0] < 2 ** 32 for txn in writes)

def test_reads_carry_no_data():
    assert all(txn.data == () for txn in txns(AxiTransactionSequenceConfig(write_pct=0)))

def test_rejects_range_without_aligned_address():
    with pytest.raises(ValueError):
        txns(AxiTransactionSequenceConfig(min_address=5, max_address=7))

def test_get_next_txn_must_be_overridden():
    with pytest.raises(NotImplementedError):
        AxiTransactionSequence.create("axi_transaction_sequence")._get_next_txn()
