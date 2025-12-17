from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import random


@dataclass(frozen=True)
class Production:
    expansion: Tuple[str, ...]

    @classmethod
    def from_tokens(cls, tokens: Sequence[str]) -> "Production":
        return cls(tuple(tokens))

    def is_terminal_only(self) -> bool:
        return all(not Grammar.is_non_terminal(token) for token in self.expansion)

    def is_self_recursive(self, symbol: str) -> bool:
        return symbol in self.expansion


@dataclass
class DerivationNode:
    symbol: str
    children: List["DerivationNode"] = field(default_factory=list)

    def is_terminal(self) -> bool:
        return not Grammar.is_non_terminal(self.symbol)

    def traverse(self) -> Iterable["DerivationNode"]:
        yield self
        for child in self.children:
            yield from child.traverse()


class GrammarError(RuntimeError):
    pass


class Grammar:
    def __init__(self, start_symbol: str, productions: Optional[Dict[str, Sequence[Sequence[str]]]] = None):
        self.start_symbol = start_symbol
        self._productions: Dict[str, List[Production]] = {}
        if productions:
            for non_terminal, rules in productions.items():
                for expansion in rules:
                    self.add_rule(non_terminal, expansion)

    @staticmethod
    def is_non_terminal(symbol: str) -> bool:
        return symbol.startswith("<") and symbol.endswith(">")

    def add_rule(self, non_terminal: str, expansion: Sequence[str]) -> None:
        production = expansion if isinstance(expansion, Production) else Production.from_tokens(expansion)
        self._productions.setdefault(non_terminal, []).append(production)

    def set_rules(self, non_terminal: str, expansions: Sequence[Sequence[str]]) -> None:
        self._productions[non_terminal] = [Production.from_tokens(ex) for ex in expansions]

    def inject_terminals(self, non_terminal: str, terminals: Sequence[str]) -> None:
        if not terminals:
            raise GrammarError(f"No terminals provided for {non_terminal}")
        cleaned = [str(term) for term in terminals]
        self._productions[non_terminal] = [Production((value,)) for value in cleaned]

    def productions_for(self, non_terminal: str) -> List[Production]:
        return self._productions.get(non_terminal, [])

    def generate(
        self,
        rng: Optional[random.Random] = None,
        max_depth: int = 6,
    ) -> DerivationNode:
        if max_depth < 1:
            raise ValueError("max_depth must be positive")
        random_generator = rng or random.Random()
        return self._expand(self.start_symbol, random_generator, depth=0, max_depth=max_depth)

    def _expand(
        self,
        symbol: str,
        rng: random.Random,
        depth: int,
        max_depth: int,
    ) -> DerivationNode:
        if not self.is_non_terminal(symbol):
            return DerivationNode(symbol=symbol, children=[])

        productions = self.productions_for(symbol)
        if not productions:
            raise GrammarError(f"No productions registered for symbol {symbol}")

        options = self._eligible_productions(symbol, productions, depth, max_depth)
        production = rng.choice(options)
        children = [
            self._expand(token, rng, depth + 1, max_depth)
            for token in production.expansion
        ]
        return DerivationNode(symbol=symbol, children=children)

    def _eligible_productions(
        self,
        symbol: str,
        productions: List[Production],
        depth: int,
        max_depth: int,
    ) -> List[Production]:
        if depth < max_depth:
            return productions

        terminal_only = [prod for prod in productions if prod.is_terminal_only()]
        if terminal_only:
            return terminal_only

        non_recursive = [prod for prod in productions if not prod.is_self_recursive(symbol)]
        return non_recursive or productions


def build_arithmetic_grammar(
    variables: Sequence[str],
    constants: Sequence[float | int | str],
    operations: Optional[Sequence[str]] = None,
) -> Grammar:
    grammar = Grammar("<expr>")
    grammar.add_rule("<expr>", ("<operation>",))
    grammar.add_rule("<expr>", ("<var>",))
    grammar.add_rule("<expr>", ("<const>",))
    grammar.add_rule("<operation>", ("<op>", "<expr>", "<expr>"))

    grammar.inject_terminals("<var>", variables)
    grammar.inject_terminals("<const>", [str(value) for value in constants])
    grammar.inject_terminals("<op>", operations or ["+", "-", "*", "/"])
    return grammar
