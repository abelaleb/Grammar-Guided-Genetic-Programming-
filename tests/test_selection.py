import random

from gggp.complexity import ComplexityMetrics
from gggp.grammar import DerivationNode
from gggp.individual import Individual
from gggp.selection import prefer_fittest, tournament_selection
from gggp.tree import ExpressionNode


def _constant_individual(node_count: int, fitness: float) -> Individual:
    individual = Individual(
        derivation=DerivationNode("<expr>"),
        expression=ExpressionNode("constant", "1"),
        complexity=ComplexityMetrics(node_count=node_count, depth=1, terminal_count=1),
    )
    individual.adjusted_fitness = fitness
    return individual


def test_prefer_fittest_breaks_ties_with_complexity():
    better_fitness = _constant_individual(node_count=5, fitness=1.0)
    worse_fitness = _constant_individual(node_count=5, fitness=0.5)
    assert prefer_fittest(better_fitness, worse_fitness) is better_fitness

    tie_simple = _constant_individual(node_count=3, fitness=0.7)
    tie_complex = _constant_individual(node_count=9, fitness=0.7)
    assert prefer_fittest(tie_simple, tie_complex) is tie_simple


def test_tournament_selection_uses_preference_logic():
    population = [
        _constant_individual(7, 0.1),
        _constant_individual(6, 0.3),
        _constant_individual(5, 0.3),  # should be preferred among ties
        _constant_individual(8, 0.2),
    ]
    rng = random.Random(5)
    winner = tournament_selection(population, tournament_size=3, rng=rng)
    assert winner.adjusted_fitness >= 0.3
