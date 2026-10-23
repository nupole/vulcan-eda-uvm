import pytest

from vulcan_eda.uvm.configs.sequences.transaction_sequence_config import TransactionSequenceConfig

def test_defaults():
    assert TransactionSequenceConfig() == TransactionSequenceConfig(txn_pct=100, max_num_txn=10)

@pytest.mark.parametrize("txn_pct", [-1, 101])
def test_rejects_txn_pct_out_of_range(txn_pct):
    with pytest.raises(ValueError):
        TransactionSequenceConfig(txn_pct=txn_pct)

@pytest.mark.parametrize("max_num_txn", [-1, 0])
def test_rejects_max_num_txn_not_positive(max_num_txn):
    with pytest.raises(ValueError):
        TransactionSequenceConfig(max_num_txn=max_num_txn)
