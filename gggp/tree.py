from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from .grammar import DerivationNode, Grammar


def _safe_division(left: float, right: float) -> float:
    """Divide two numbers while guarding against near-zero denominators."""
    if abs(right) < 1e-12:
        raise ZeroDivisionError("Division by zero in expression evaluation")
    return left / right


OPERATORS: Dict[str, Callable[[float, float], float]] = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": _safe_division,
}


@dataclass
class ExpressionNode:
    """Evaluatable node in an arithmetic expression tree."""
    kind: str
    value: str | float
    children: List["ExpressionNode"] = field(default_factory=list)

    def evaluate(self, context: Dict[str, float]) -> float:
        """Evaluate this node using the provided variable assignments."""
        if self.kind == "variable":
            if self.value not in context:
                raise KeyError(f"Variable {self.value} missing from context")
            return float(context[self.value])

        if self.kind == "constant":
            return float(self.value)

        if self.kind == "operator":
            if self.value not in OPERATORS:
                raise ValueError(f"Operator {self.value} not registered")
            if len(self.children) != 2:
                raise ValueError("Operator nodes require exactly two operands")
            left = self.children[0].evaluate(context)
            right = self.children[1].evaluate(context)
            return OPERATORS[self.value](left, right)

        raise ValueError(f"Unsupported expression node kind {self.kind}")

    def collect_variables(self) -> List[str]:
        """Return all variable identifiers referenced below this node."""
        if self.kind == "variable":
            return [str(self.value)]
        result: List[str] = []
        for child in self.children:
            result.extend(child.collect_variables())
        return result

    def __str__(self) -> str:
        """Render the node as an infix string for debugging."""
        if self.kind == "operator":
            return f"({self.children[0]} {self.value} {self.children[1]})"
        return str(self.value)


class ArithmeticTreeBuilder:
    """Convert derivation trees into executable arithmetic expression trees."""
    def build(self, derivation: DerivationNode) -> ExpressionNode:
        """Public entrypoint that builds an ExpressionNode tree."""
        return self._convert(derivation)

    def _convert(self, node: DerivationNode) -> ExpressionNode:
        """Recursively translate a derivation node into an ExpressionNode."""
        if node.symbol == "<expr>":
            if not node.children:
                raise ValueError("<expr> nodes must have children")
            return self._convert(node.children[0])

        if node.symbol == "<operation>":
            if len(node.children) != 3:
                raise ValueError("<operation> expects <op> and two <expr> children")
            operator = self._extract_token(node.children[0])
            left = self._convert(node.children[1])
            right = self._convert(node.children[2])
            return ExpressionNode("operator", operator, [left, right])

        if node.symbol == "<var>":
            return ExpressionNode("variable", self._extract_token(node.children[0]))

        if node.symbol == "<const>":
            return ExpressionNode("constant", self._extract_token(node.children[0]))

        if node.symbol == "<op>":
            return ExpressionNode("operator-token", self._extract_token(node.children[0]))

        if not Grammar.is_non_terminal(node.symbol):
            return ExpressionNode("literal", node.symbol)

        if len(node.children) == 1:
            return self._convert(node.children[0])

        raise ValueError(f"Unhandled node symbol {node.symbol}")

    def _extract_token(self, node: DerivationNode) -> str:
        """Extract the literal token stored at a derivation node."""
        if not node.children and not Grammar.is_non_terminal(node.symbol):
            return node.symbol
        if node.children:
            return self._extract_token(node.children[0])
        raise ValueError("Unable to extract token from node")
