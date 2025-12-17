from __future__ import annotations

from typing import Iterable, List, Optional
import random

from .individual import Individual


def prefer_fittest(individual_a: Individual, individual_b: Individual, tolerance: float = 1e-12) -> Individual:
    if individual_a.adjusted_fitness is None or individual_b.adjusted_fitness is None:
        raise ValueError("Individuals must be evaluated before comparison")

    diff = individual_a.adjusted_fitness - individual_b.adjusted_fitness
    if diff > tolerance:
        return individual_a
    if diff < -tolerance:
        return individual_b

    return (
        individual_a
        if individual_a.complexity <= individual_b.complexity
        else individual_b
    )


def tournament_selection(
    population: Iterable[Individual],
    tournament_size: int = 3,
    rng: Optional[random.Random] = None,
) -> Individual:
    participants = list(population)
    if len(participants) < tournament_size:
        raise ValueError("Tournament size cannot exceed population size")
    random_generator = rng or random.Random()
    contenders = random_generator.sample(participants, tournament_size)
    winner = contenders[0]
    for contender in contenders[1:]:
        winner = prefer_fittest(winner, contender)
    return winner
