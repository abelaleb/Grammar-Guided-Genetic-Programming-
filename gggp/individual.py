from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import random

from .grammar import DerivationNode, Grammar
from .tree import ArithmeticTreeBuilder, ExpressionNode
from .complexity import ComplexityMetrics, compute_metrics


@dataclass
class Individual:
    derivation: DerivationNode
    expression: ExpressionNode
    complexity: ComplexityMetrics
    raw_fitness: Optional[float] = field(default=None)
    adjusted_fitness: Optional[float] = field(default=None)

    @classmethod
    def generate(
        cls,
        grammar: Grammar,
        rng: Optional[random.Random] = None,
        max_depth: int = 6,
        builder: Optional[ArithmeticTreeBuilder] = None,
    ) -> "Individual":
        random_generator = rng or random.Random()
        tree_builder = builder or ArithmeticTreeBuilder()
        derivation = grammar.generate(random_generator, max_depth=max_depth)
        expression = tree_builder.build(derivation)
        metrics = compute_metrics(derivation)
        return cls(derivation=derivation, expression=expression, complexity=metrics)

    def evaluate(self, evaluator: "FitnessEvaluator") -> float:
        from .fitness import FitnessEvaluator  # local import to avoid circular dependency

        if not isinstance(evaluator, FitnessEvaluator):
            raise TypeError("evaluator must be a FitnessEvaluator")
        return evaluator.evaluate(self)
