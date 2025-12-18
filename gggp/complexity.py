from __future__ import annotations

from dataclasses import dataclass

from .grammar import DerivationNode, Grammar


@dataclass(order=True)
class ComplexityMetrics:
    """Lightweight container capturing tree size, depth, and terminal count."""
    node_count: int
    depth: int
    terminal_count: int

    def scalar(self) -> float:
        return float(self.node_count)


def compute_metrics(node: DerivationNode) -> ComplexityMetrics:
    """Compute structural complexity statistics for a derivation tree."""
    node_count, depth, terminal_count = _metrics(node)
    return ComplexityMetrics(node_count=node_count, depth=depth, terminal_count=terminal_count)


def _metrics(node: DerivationNode) -> tuple[int, int, int]:
    if not node.children:
        terminal = 0 if Grammar.is_non_terminal(node.symbol) else 1
        return 1, 1, terminal

    child_metrics = [_metrics(child) for child in node.children]
    node_count = 1 + sum(count for count, _, _ in child_metrics)
    depth = 1 + max(depth for _, depth, _ in child_metrics)
    terminal_count = sum(terminals for _, _, terminals in child_metrics)
    return node_count, depth, terminal_count
