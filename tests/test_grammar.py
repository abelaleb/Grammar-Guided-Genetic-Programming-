import random

from gggp.grammar import build_arithmetic_grammar
from gggp.tree import ArithmeticTreeBuilder


def test_grammar_injects_terminals_and_generates_valid_expression():
    variables = ["x1", "x2"]
    constants = [1, 2]
    grammar = build_arithmetic_grammar(variables, constants)
    builder = ArithmeticTreeBuilder()

    derivation = grammar.generate(random.Random(7), max_depth=4)
    expression = builder.build(derivation)
    variables_used = set(expression.collect_variables())
    assert variables_used.issubset(set(variables))

    grammar.inject_terminals("<var>", ["x3", "x4"])
    injected = {production.expansion[0] for production in grammar.productions_for("<var>")}
    assert injected == {"x3", "x4"}
