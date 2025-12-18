from gggp.complexity import ComplexityMetrics
from gggp.fitness import FitnessCase, FitnessEvaluator
from gggp.grammar import DerivationNode
from gggp.individual import Individual
from gggp.tree import ExpressionNode


def _expression_x_plus_const(constant: float) -> ExpressionNode:
    return ExpressionNode(
        "operator",
        "+",
        [
            ExpressionNode("variable", "x0"),
            ExpressionNode("constant", str(constant)),
        ],
    )


def test_parsimony_penalty_favors_simpler_expression():
    expression = _expression_x_plus_const(1.0)
    base_cases = [
        FitnessCase(inputs={"x0": 0.0}, target=1.0),
        FitnessCase(inputs={"x0": 1.0}, target=2.0),
    ]
    evaluator = FitnessEvaluator(base_cases, penalty_coefficient=0.1)

    simple = Individual(
        derivation=DerivationNode("<expr>"),
        expression=expression,
        complexity=ComplexityMetrics(node_count=3, depth=2, terminal_count=2),
    )
    complex_version = Individual(
        derivation=DerivationNode("<expr>"),
        expression=expression,
        complexity=ComplexityMetrics(node_count=10, depth=5, terminal_count=2),
    )

    simple_score = evaluator.evaluate(simple)
    complex_score = evaluator.evaluate(complex_version)

    assert simple.raw_fitness == complex_version.raw_fitness
    assert simple_score > complex_score
    print("test_parsimony_penalty_favors_simpler_expression passed")
