import random

from gggp.grammar import build_arithmetic_grammar
from gggp.individual import Individual


def test_individual_generation_creates_evaluable_expression():
    grammar = build_arithmetic_grammar(["x0"], [1])
    individual = Individual.generate(grammar, rng=random.Random(3), max_depth=5)
    value = individual.expression.evaluate({"x0": 2.5})
    assert isinstance(value, float)
