from _wagyu import IntersectNode
from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.intersect_nodes)
def test_reflexivity(intersect_node: IntersectNode) -> None:
    assert intersect_node == intersect_node


@given(strategies.intersect_nodes, strategies.intersect_nodes)
def test_symmetry(first_intersect_node: IntersectNode,
                  second_intersect_node: IntersectNode) -> None:
    assert equivalence(first_intersect_node == second_intersect_node,
                       second_intersect_node == first_intersect_node)


@given(strategies.intersect_nodes, strategies.intersect_nodes,
       strategies.intersect_nodes)
def test_transitivity(first_intersect_node: IntersectNode,
                      second_intersect_node: IntersectNode,
                      third_intersect_node: IntersectNode) -> None:
    assert implication(first_intersect_node == second_intersect_node
                       and second_intersect_node == third_intersect_node,
                       first_intersect_node == third_intersect_node)


@given(strategies.intersect_nodes, strategies.intersect_nodes)
def test_connection_with_inequality(first_intersect_node: IntersectNode,
                                    second_intersect_node: IntersectNode
                                    ) -> None:
    assert equivalence(not first_intersect_node == second_intersect_node,
                       first_intersect_node != second_intersect_node)
