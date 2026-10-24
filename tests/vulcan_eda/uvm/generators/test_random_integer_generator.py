import dataclasses
import itertools
import random

import pytest

from vulcan_eda.uvm.generators import RandomIntegerGenerator

def take(generator, count):
    return list(itertools.islice(generator, count))

def test_yields_every_value_in_the_inclusive_range():
    assert set(take(RandomIntegerGenerator(-2, 2), 500)) == {-2, -1, 0, 1, 2}

def test_equal_bounds_yield_that_value():
    assert take(RandomIntegerGenerator(7, 7), 3) == [7, 7, 7]

def test_seed_makes_every_iteration_identical():
    random_integer_generator = RandomIntegerGenerator(0, 2 ** 32, seed=1)
    assert take(random_integer_generator, 20) == take(random_integer_generator, 20)

def test_different_seeds_differ():
    assert take(RandomIntegerGenerator(0, 2 ** 32, seed=1), 20) != take(RandomIntegerGenerator(0, 2 ** 32, seed=2), 20)

def test_without_seed_each_iteration_differs():
    random_integer_generator = RandomIntegerGenerator(0, 2 ** 32)
    assert take(random_integer_generator, 20) != take(random_integer_generator, 20)

def test_without_seed_follows_the_global_seed():
    random_integer_generator = RandomIntegerGenerator(0, 2 ** 32)
    random.seed(3)
    first = take(random_integer_generator, 20)
    random.seed(3)
    assert take(random_integer_generator, 20) == first

def test_rejects_min_value_greater_than_max_value():
    with pytest.raises(ValueError):
        RandomIntegerGenerator(2, 1)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        RandomIntegerGenerator(0, 1).seed = 1

def test_repr_shows_its_fields():
    assert repr(RandomIntegerGenerator(0, 255, seed=4)) == "RandomIntegerGenerator(min_value=0, max_value=255, seed=4)"
