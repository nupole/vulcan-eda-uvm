import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import PrbsGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

PRBS7 = "0000001000001100001010001111001000101100111010100111110100001110001001001101101011011110110001101001011101110011001010101111111"

def repeats_every(bits, length):
    return bits[length:] == bits[:-length]

@pytest.mark.parametrize("order", [7, 9, 11, 15])
def test_has_the_maximal_period(order):
    maximal_period = 2 ** order - 1
    bits = take(PrbsGenerator(order), 2 * maximal_period)
    assert repeats_every(bits, maximal_period)
    assert not any(repeats_every(bits, length) for length in range(1, maximal_period) if maximal_period % length == 0)

@pytest.mark.parametrize("order", [7, 9, 11, 15])
def test_each_period_has_one_more_one_than_zeros(order):
    bits = take(PrbsGenerator(order), 2 ** order - 1)
    assert sum(bits) == 2 ** (order - 1)

@pytest.mark.parametrize("order", [23, 31])
def test_long_orders_do_not_repeat_early(order):
    bits = take(PrbsGenerator(order), 2000)
    assert not any(repeats_every(bits, length) for length in range(1, 1000))

def test_matches_the_published_prbs7_sequence():
    assert "".join(map(str, take(PrbsGenerator(7), 127))) == PRBS7

def test_yields_bits_by_default():
    assert set(take(PrbsGenerator(7), 127)) == {0, 1}

def test_words_pack_consecutive_bits_msb_first():
    bits = take(PrbsGenerator(7), 32)
    words = take(PrbsGenerator(7, width=8), 4)
    assert words == [int("".join(map(str, bits[index:index + 8])), 2) for index in range(0, 32, 8)]

def test_start_changes_the_phase_not_the_sequence():
    reference = take(PrbsGenerator(7), 254)
    shifted = take(PrbsGenerator(7, start=1), 127)
    assert any(reference[offset:offset + 127] == shifted for offset in range(127))

def test_each_iteration_is_independent():
    prbs_generator = PrbsGenerator(7)
    first = iter(prbs_generator)
    next(first)
    assert take(prbs_generator, 20) == take(PrbsGenerator(7), 20)

@pytest.mark.parametrize("order", [0, 8, 32])
def test_rejects_unsupported_order(order):
    with pytest.raises(ValueError):
        PrbsGenerator(order)

@pytest.mark.parametrize("width", [-1, 0])
def test_rejects_width_not_positive(width):
    with pytest.raises(ValueError):
        PrbsGenerator(width=width)

@pytest.mark.parametrize("start", [0, 128])
def test_rejects_start_zero_or_too_wide(start):
    with pytest.raises(ValueError):
        PrbsGenerator(7, start=start)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        PrbsGenerator().order = 9

def test_repr_shows_its_fields():
    assert repr(PrbsGenerator(15, width=32)) == "PrbsGenerator(order=15, width=32, start=None)"
