# Grammar-Guided Genetic Programming (GGGP)

This repository provides a modular Python implementation of grammar-guided genetic programming featuring:

- A runtime-configurable context-free grammar with terminal injection for arbitrary variable sets.
- Derivation trees that map cleanly onto evaluable expression trees.
- Complexity metrics (node count, depth, terminal count) with parsimony pressure baked into fitness evaluation.
- Selection utilities that break fitness ties via complexity-aware comparisons.
- A comprehensive unit test suite covering grammar expansion, individual generation, fitness scoring, complexity tracking, and selection logic.

Run the test suite with:

```bash
pytest
```
