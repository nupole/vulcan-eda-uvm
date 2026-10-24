import dataclasses
import random

import pytest

from vulcan_eda.uvm.generators import RandomGenerator

from tests.support.generators import take

@dataclasses.dataclass(frozen=True)
class WordGenerator(RandomGenerator):
    def next_value(self, rng):
        return rng.getrandbits(32)

def test_seed_makes_every_iteration_identical():
    word_generator = WordGenerator(seed=1)
    assert take(word_generator, 20) == take(word_generator, 20)

def test_different_seeds_differ():
    assert take(WordGenerator(seed=1), 20) != take(WordGenerator(seed=2), 20)

def test_without_seed_each_iteration_differs():
    word_generator = WordGenerator()
    assert take(word_generator, 20) != take(word_generator, 20)

def test_without_seed_follows_the_global_seed():
    word_generator = WordGenerator()
    random.seed(3)
    first = take(word_generator, 20)
    random.seed(3)
    assert take(word_generator, 20) == first

def test_seed_is_keyword_only():
    with pytest.raises(TypeError):
        WordGenerator(1)

def test_next_value_must_be_overridden():
    with pytest.raises(NotImplementedError):
        next(iter(RandomGenerator()))
