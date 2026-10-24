import dataclasses
import itertools

import pytest

from vulcan_eda.uvm.generators import RandomGenerator, RandomBooleanGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_is_a_random_generator():
    assert isinstance(RandomBooleanGenerator(50), RandomGenerator)

def test_yields_booleans():
    assert set(take(RandomBooleanGenerator(50), 100)) == {False, True}

def test_100_percent_is_always_true():
    assert all(take(RandomBooleanGenerator(100), 1000))

@pytest.mark.parametrize("pct_true", [10, 50, 90])
def test_true_about_pct_true_of_the_time(pct_true):
    values = take(RandomBooleanGenerator(pct_true, seed=1), 10000)
    assert abs(100 * sum(values) / len(values) - pct_true) < 2

def test_accepts_fractional_pct_true():
    values = take(RandomBooleanGenerator(0.5, seed=1), 100000)
    assert 0.3 < 100 * sum(values) / len(values) < 0.7

def test_seed_makes_every_iteration_identical():
    random_boolean_generator = RandomBooleanGenerator(50, seed=1)
    assert take(random_boolean_generator, 20) == take(random_boolean_generator, 20)

@pytest.mark.parametrize("pct_true", [-1, 0, 100.5])
def test_rejects_pct_true_out_of_range(pct_true):
    with pytest.raises(ValueError):
        RandomBooleanGenerator(pct_true)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        RandomBooleanGenerator(50).pct_true = 10

def test_repr_shows_its_fields():
    assert repr(RandomBooleanGenerator(50, seed=4)) == "RandomBooleanGenerator(seed=4, pct_true=50)"
