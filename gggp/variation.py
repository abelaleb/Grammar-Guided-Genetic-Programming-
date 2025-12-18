# gggp/variation.py

from __future__ import annotations
import random
from typing import Optional

from .grammar import DerivationNode, Grammar
from .individual import Individual
from .tree import ArithmeticTreeBuilder
from .complexity import compute_metrics


def random_subtree(node: DerivationNode, rng: random.Random) -> DerivationNode:
    """Pick a random node from the derivation tree."""
    nodes = list(node.traverse())
    return rng.choice(nodes)


def clone_tree(node: DerivationNode) -> DerivationNode:
    """Deep copy a derivation tree."""
    return DerivationNode(
        symbol=node.symbol,
        children=[clone_tree(child) for child in node.children]
    )


def replace_subtree(root: DerivationNode, target: DerivationNode, replacement: DerivationNode) -> DerivationNode:
    """Return a copy of root where the target node is replaced with replacement."""
    if root is target:
        return clone_tree(replacement)
    return DerivationNode(
        symbol=root.symbol,
        children=[replace_subtree(child, target, replacement) for child in root.children]
    )


def crossover(
    parent_a: Individual,
    parent_b: Individual,
    rng: Optional[random.Random] = None,
    builder: Optional[ArithmeticTreeBuilder] = None,
) -> Individual:
    """Swap random subtrees between two parents to create a child."""
    rng = rng or random.Random()
    builder = builder or ArithmeticTreeBuilder()

    a_tree = clone_tree(parent_a.derivation)
    b_tree = clone_tree(parent_b.derivation)

    a_sub = random_subtree(a_tree, rng)
    b_sub = random_subtree(b_tree, rng)

    child_tree = replace_subtree(a_tree, a_sub, b_sub)
    child_expr = builder.build(child_tree)
    child_complexity = compute_metrics(child_tree)

    return Individual(
        derivation=child_tree,
        expression=child_expr,
        complexity=child_complexity
    )


def mutation(
    parent: Individual,
    grammar: Grammar,
    rng: Optional[random.Random] = None,
    max_depth: int = 4,
    builder: Optional[ArithmeticTreeBuilder] = None,
) -> Individual:
    """Regrow a random subtree using the grammar to introduce new genetic material."""
    rng = rng or random.Random()
    builder = builder or ArithmeticTreeBuilder()

    tree = clone_tree(parent.derivation)
    target = random_subtree(tree, rng)

    new_subtree = grammar.generate(rng, max_depth=max_depth)
    mutated_tree = replace_subtree(tree, target, new_subtree)

    expr = builder.build(mutated_tree)
    complexity = compute_metrics(mutated_tree)

    return Individual(
        derivation=mutated_tree,
        expression=expr,
        complexity=complexity
    )
