# run.py

import random

from gggp.grammar import build_arithmetic_grammar
from gggp.fitness import FitnessCase, FitnessEvaluator
from gggp.population import Population


def main():
    cases = [
        FitnessCase({"x": -2}, 4),
        FitnessCase({"x": -1}, 1),
        FitnessCase({"x": 0}, 0),
        FitnessCase({"x": 1}, 1),
        FitnessCase({"x": 2}, 4),
    ]

    grammar = build_arithmetic_grammar(
        variables=["x"],
        constants=[0, 1, 2],
        operations=["+", "-", "*"]
    )

    evaluator = FitnessEvaluator(
        cases=cases,
        penalty_coefficient=0.01
    )

    pop = Population(
        grammar=grammar,
        evaluator=evaluator,
        size=100,
        rng=random.Random(42),
    )

    GENERATIONS = 30

    for gen in range(GENERATIONS):
        pop.evaluate()
        best = pop.best()
        print(
            f"Gen {gen:02d} | "
            f"Fitness={best.adjusted_fitness:.4f} | "
            f"Size={best.complexity.node_count} | "
            f"Expr={best.expression}"
        )
        pop.evolve_one_generation()


if __name__ == "__main__":
    main()
