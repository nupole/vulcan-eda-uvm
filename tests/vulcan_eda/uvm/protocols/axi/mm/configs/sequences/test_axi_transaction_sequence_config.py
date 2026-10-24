import pytest

from vulcan_eda.uvm.protocols.axi.mm.configs.sequences import AxiTransactionSequenceConfig

def test_defaults():
    assert AxiTransactionSequenceConfig() == AxiTransactionSequenceConfig(num_txn=10, write_pct=50, min_address=0, max_address=None)

@pytest.mark.parametrize("num_txn", [-1, 0])
def test_rejects_num_txn_not_positive(num_txn):
    with pytest.raises(ValueError):
        AxiTransactionSequenceConfig(num_txn=num_txn)

@pytest.mark.parametrize("write_pct", [-1, 101])
def test_rejects_write_pct_out_of_range(write_pct):
    with pytest.raises(ValueError):
        AxiTransactionSequenceConfig(write_pct=write_pct)

@pytest.mark.parametrize("write_pct", [0, 100])
def test_accepts_write_pct_bounds(write_pct):
    assert AxiTransactionSequenceConfig(write_pct=write_pct).write_pct == write_pct

def test_rejects_negative_min_address():
    with pytest.raises(ValueError):
        AxiTransactionSequenceConfig(min_address=-1)

def test_rejects_min_address_greater_than_max_address():
    with pytest.raises(ValueError):
        AxiTransactionSequenceConfig(min_address=8, max_address=4)

def test_accepts_equal_min_and_max_address():
    assert AxiTransactionSequenceConfig(min_address=4, max_address=4).max_address == 4
