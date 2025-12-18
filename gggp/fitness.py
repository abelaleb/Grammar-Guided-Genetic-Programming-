from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .tree import ExpressionNode


@dataclass(frozen=True)
class FitnessCase:
    """Single supervised learning example (inputs + expected target)."""
    inputs: dict[str, float]
    target: float


class FitnessEvaluator:
    """Compute fitness by comparing expression outputs to known targets."""
    def __init__(
        self,
        cases: Iterable[FitnessCase],
        penalty_coefficient: float = 0.0,
    ):
        self.cases: List[FitnessCase] = list(cases)
        if not self.cases:
            raise ValueError("At least one fitness case is required")
        self.penalty_coefficient = penalty_coefficient

    def evaluate_expression(self, expression: ExpressionNode) -> float:
        """Return negative MSE of the expression across all fitness cases."""
        errors: List[float] = []
        for case in self.cases:
            try:
                value = expression.evaluate(case.inputs)
            except (ZeroDivisionError, ValueError, KeyError):
                return float("-inf")
            errors.append((value - case.target) ** 2)
        mse = sum(errors) / len(errors)
        return -mse

    def evaluate(self, individual: "Individual") -> float:
        """Evaluate an individual, storing raw and adjusted fitness scores."""
        from .individual import Individual  # local import to prevent circular dependency
        if not isinstance(individual, Individual):
            raise TypeError("Expected an Individual instance")
        raw_fitness = self.evaluate_expression(individual.expression)
        penalty = self.penalty_coefficient * individual.complexity.scalar()
        adjusted_fitness = raw_fitness - penalty
        individual.raw_fitness = raw_fitness
        individual.adjusted_fitness = adjusted_fitness
        return adjusted_fitness

    def with_penalty(self, penalty_coefficient: float) -> "FitnessEvaluator":
        """Return a copy of this evaluator with a different penalty coefficient."""
        clone = FitnessEvaluator(self.cases, penalty_coefficient=penalty_coefficient)
        return clone
