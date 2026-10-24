import dataclasses

import pytest

from vulcan_eda.uvm.protocols.axi.mm.data import AxiBurst, AxiResponse, AxiTransaction

def test_defaults_are_a_single_beat_incr_with_id_zero():
    read = AxiTransaction(access=AxiTransaction.Access.READ, address=0x10)
    assert (read.data, read.num_beats, read.id, read.burst, read.response) == ((), 1, 0, AxiBurst.INCR, None)

def test_completes_a_read_with_replace():
    read = AxiTransaction(access=AxiTransaction.Access.READ, address=0x10)
    completed = dataclasses.replace(read, data=(0x1234,), response=AxiResponse.OKAY)
    assert (completed.data, completed.response) == ((0x1234,), AxiResponse.OKAY)

def test_rejects_num_beats_not_positive():
    with pytest.raises(ValueError):
        AxiTransaction(access=AxiTransaction.Access.READ, address=0x10, num_beats=0)

@pytest.mark.parametrize("data", [(), (1, 2)])
def test_rejects_write_without_one_word_per_beat(data):
    with pytest.raises(ValueError):
        AxiTransaction(access=AxiTransaction.Access.WRITE, address=0x10, data=data)

def test_rejects_read_with_wrong_number_of_words():
    with pytest.raises(ValueError):
        AxiTransaction(access=AxiTransaction.Access.READ, address=0x10, data=(1, 2))

def test_is_keyword_only():
    with pytest.raises(TypeError):
        AxiTransaction(AxiTransaction.Access.READ, 0x10)
