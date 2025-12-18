# Grammar-Guided Genetic Programming (GGGP)

This codebase implements a compact, fully modular grammar-guided genetic programming (GGGP) engine.  It lets you define a context-free grammar, evolve derivation trees sampled from that grammar, translate them into arithmetic expression trees, and score/evolve them with standard evolutionary operators.  The repository is intentionally small so each subsystem can be read, tweaked, or swapped independently.

## Repository layout

| Path | Purpose |
| --- | --- |
| `run.py` | Wires every subsystem together for a ready-to-run experiment that rediscovers the polynomial `x²` from noisy observations. |
| `gggp/grammar.py` | Grammar management: production rules, derivation-tree sampling, and helper constructors such as `build_arithmetic_grammar`. |
| `gggp/tree.py` | Converts derivation trees into executable arithmetic expression trees built from `ExpressionNode` instances. |
| `gggp/complexity.py` | Computes structural metrics (node count, depth, terminal count) that feed parsimony pressure. |
| `gggp/individual.py` | Represents an individual (derivation, expression, complexity, fitness cache) and exposes a `generate` helper. |
| `gggp/fitness.py` | Defines `FitnessCase` plus `FitnessEvaluator`, which scores expressions via negative mean squared error with optional penalties. |
| `gggp/selection.py` | Provides deterministic tie-breaking (`prefer_fittest`) and tournament selection. |
| `gggp/variation.py` | Houses subtree crossover, point mutation, and tree-cloning utilities. |
| `gggp/population.py` | Maintains a population, evaluates it, and drives generational evolution. |

## Pipeline walk-through (`run.py`)

1. **Define supervised cases** – `FitnessCase` pairs (`{"x": value}`, `target`) encode samples from `x²`.  
2. **Build the grammar** – `build_arithmetic_grammar` injects variables, constants, and operators so `<expr>` can expand into binary operator trees, variable leaves, or constants.  
3. **Instantiate the evaluator** – `FitnessEvaluator` scores each expression by negative MSE across the dataset and subtracts a size-based penalty to discourage bloat.  
4. **Seed the population** – `Population` samples derivations with bounded depth, converts them to executable expressions, and caches complexity metrics.  
5. **Evolution loop** – For each generation:  
   - Evaluate everyone, caching raw/adjusted fitness.  
   - Report the current best individual (fitness, tree size, infix expression).  
   - Create the next generation via tournament selection plus crossover or mutation (rates configurable on the `Population`).  
   - Repeat for the requested number of generations.

Because `run.py` threads the same RNG through every subsystem, the sample experiment is reproducible—handy when testing tweaks to the grammar, operators, or evaluator.

## Module details

### `gggp/grammar.py`
- `Grammar` stores productions keyed by non-terminal symbols.  It can inject terminals on the fly, enforce maximum depth, and bias toward terminating expansions when deep in the tree.  
- `Production` encapsulates an expansion and exposes helpers like `is_terminal_only` (used for depth control).  
- `DerivationNode` represents nodes in a derivation tree and supports pre-order traversal; most subsystems manipulate or clone these nodes.  
- `build_arithmetic_grammar` is a convenience constructor for arithmetic expressions with `<expr>`, `<operation>`, `<var>`, `<const>`, and `<op>` symbols.

### `gggp/tree.py`
- `ExpressionNode` evaluates itself recursively, handling typed nodes (`variable`, `constant`, `operator`).  Operators use a guarded dictionary (division checks near-zero denominators).  
- `ArithmeticTreeBuilder` walks a derivation tree and emits an equivalent expression tree, validating structural expectations along the way.  This translation layer keeps grammar concerns separate from evaluation concerns.

### `gggp/complexity.py`
- `compute_metrics` traverses a derivation tree, counting nodes, depth, and terminal leaves.  
- `ComplexityMetrics` is `@dataclass(order=True)`, enabling comparisons when breaking fitness ties, and offers a `scalar()` helper currently mapped to node count.

### `gggp/individual.py`
- `Individual.generate` samples a derivation with the grammar, converts it to an expression, and records complexity metrics in one shot.  
- `Individual.evaluate` simply delegates to `FitnessEvaluator`, ensuring type safety and caching both raw and adjusted fitness values.

### `gggp/fitness.py`
- `FitnessEvaluator.evaluate_expression` runs an expression across every `FitnessCase` and returns negative MSE; invalid expressions (division by zero, missing variables, etc.) receive `-inf`.  
- `evaluate` subtracts a penalty proportional to `ComplexityMetrics.scalar`, enabling parsimony pressure.  A `with_penalty` helper makes it easy to clone evaluators with different penalties.

### `gggp/selection.py`
- `prefer_fittest` compares two evaluated individuals, using a tolerance to account for floating point noise and falling back to structural complexity for tie-breaking.  
- `tournament_selection` samples contenders uniformly at random and repeatedly applies `prefer_fittest` to choose a parent.

### `gggp/variation.py`
- `random_subtree`, `clone_tree`, and `replace_subtree` provide the plumbing needed for safe tree edits.  
- `crossover` swaps randomly chosen subtrees between two parents, rebuilds the resulting expression tree, and recomputes complexity.  
- `mutation` regenerates a subtree from scratch by re-invoking the grammar, again rebuilding and recomputing metrics before returning the child.

### `gggp/population.py`
- Handles population initialization, evaluation, and generation turnover.  
- During `evolve_one_generation`, crossover occurs with probability `crossover_rate`; otherwise mutation fires.  Every new child is appended until the next generation reaches the configured size.

## Example: rediscovering `x²`

1. Create and activate a virtual environment (optional but recommended).  
2. Install dependencies (standard library only is required, so this step can be skipped unless you add packages).  
3. Run the ready-made experiment:

```bash
python run.py
```

You should see output similar to:

```
Gen 00 | Fitness=-8.0000 | Size=5 | Expr=((x * x) + 1)
Gen 05 | Fitness=-0.2500 | Size=3 | Expr=(x * x)
Gen 10 | Fitness=-0.0000 | Size=3 | Expr=(x * x)
...
```

Each line shows the generation index, adjusted fitness (closer to zero is better because we maximize negative MSE minus penalty), current tree size, and the infix expression.  As generations progress, the engine typically converges to `(x * x)` or algebraic equivalents that fit the provided cases.

## Smoke test

The simplest smoke test is to execute `python run.py` and confirm that:

1. A population is created without errors (validating grammar generation, tree building, and metric computation).  
2. Each generation prints a best individual with finite fitness (exercise expression evaluation, fitness scoring, and parsimony penalty).  
3. Fitness improves or stays stable across generations (verifying selection plus crossover/mutation wiring).

Because the script seeds its RNG (`random.Random(42)`), the smoke test is deterministic—any deviation (crashes, `-inf` fitness across the board, unstable outputs) indicates that a recent change broke the pipeline.  For deeper assurance you can turn the smoke test into an automated check by running `python run.py > /tmp/smoke.log` in CI and diffing the best-expression trace, but the manual run is usually sufficient while developing new operators or grammars.
