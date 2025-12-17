from gggp.complexity import compute_metrics
from gggp.grammar import DerivationNode


def test_complexity_metrics_reflect_depth_and_size():
    shallow = DerivationNode(
        "<expr>",
        [DerivationNode("<const>", [DerivationNode("1")])],
    )

    deep = DerivationNode(
        "<expr>",
        [
            DerivationNode(
                "<operation>",
                [
                    DerivationNode("<op>", [DerivationNode("+")]),
                    DerivationNode("<expr>", [DerivationNode("<const>", [DerivationNode("1")])]),
                    DerivationNode("<expr>", [DerivationNode("<const>", [DerivationNode("2")])]),
                ],
            )
        ],
    )

    shallow_metrics = compute_metrics(shallow)
    deep_metrics = compute_metrics(deep)

    assert deep_metrics.node_count > shallow_metrics.node_count
    assert deep_metrics.depth > shallow_metrics.depth
