# gggp/population.py

from __future__ import annotations
import random
from typing import List

from .individual import Individual
from .fitness import FitnessEvaluator
from .selection import tournament_selection
from .variation import crossover, mutation
from .grammar import Grammar


class Population:
    """Maintain and evolve a pool of Individuals via crossover and mutation."""
    def __init__(
        self,
        grammar: Grammar,
        evaluator: FitnessEvaluator,
        size: int = 50,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        max_depth: int = 6,
        rng: random.Random | None = None,
    ):
        self.grammar = grammar
        self.evaluator = evaluator
        self.size = size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.max_depth = max_depth
        self.rng = rng or random.Random()

        self.individuals: List[Individual] = [
            Individual.generate(grammar, rng=self.rng, max_depth=max_depth)
            for _ in range(size)
        ]

    def evaluate(self) -> None:
        """Evaluate every individual in the population."""
        for ind in self.individuals:
            ind.evaluate(self.evaluator)

    def best(self) -> Individual:
        """Return the current best individual (highest adjusted fitness)."""
        return max(self.individuals, key=lambda i: i.adjusted_fitness)

    def evolve_one_generation(self) -> None:
        """Produce a new generation via tournament selection and variation."""
        new_population: List[Individual] = []

        while len(new_population) < self.size:
            if self.rng.random() < self.crossover_rate:
                p1 = tournament_selection(self.individuals, rng=self.rng)
                p2 = tournament_selection(self.individuals, rng=self.rng)
                child = crossover(p1, p2, rng=self.rng) 
            else:
                p = tournament_selection(self.individuals, rng=self.rng)
                child = mutation(
                    p,
                    grammar=self.grammar,
                    rng=self.rng,
                    max_depth=self.max_depth,
                )

            new_population.append(child)

        self.individuals = new_population
