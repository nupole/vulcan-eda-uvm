import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import RandomBitsGenerator, RandomGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_is_a_random_generator():
    assert isinstance(RandomBitsGenerator(8), RandomGenerator)

def test_yields_every_value_of_its_width():
    assert set(take(RandomBitsGenerator(2), 500)) == {0, 1, 2, 3}

def test_values_fit_in_wide_widths():
    assert all(0 <= value < 2 ** 512 for value in take(RandomBitsGenerator(512), 100))

def test_wide_values_use_the_top_bit():
    assert any(value >> 511 for value in take(RandomBitsGenerator(512), 100))

def test_seed_makes_every_iteration_identical():
    random_bits_generator = RandomBitsGenerator(32, seed=1)
    assert take(random_bits_generator, 20) == take(random_bits_generator, 20)

@pytest.mark.parametrize("width", [-1, 0])
def test_rejects_width_not_positive(width):
    with pytest.raises(ValueError):
        RandomBitsGenerator(width)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        RandomBitsGenerator(8).width = 16

def test_repr_shows_its_fields():
    assert repr(RandomBitsGenerator(8, seed=4)) == "RandomBitsGenerator(seed=4, width=8)"
