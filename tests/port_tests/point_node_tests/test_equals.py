from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.point_node import PointNode
from . import strategies


@given(strategies.points_nodes)
def test_reflexivity(point_node: PointNode) -> None:
    assert point_node == point_node


@given(strategies.points_nodes, strategies.points_nodes)
def test_symmetry(first_point: PointNode,
                  second_point: PointNode) -> None:
    assert equivalence(first_point == second_point,
                       second_point == first_point)


@given(strategies.points_nodes, strategies.points_nodes,
       strategies.points_nodes)
def test_transitivity(first_point: PointNode, second_point: PointNode,
                      third_point: PointNode) -> None:
    assert implication(first_point == second_point
                       and second_point == third_point,
                       first_point == third_point)


@given(strategies.points_nodes, strategies.points_nodes)
def test_connection_with_inequality(first_point: PointNode,
                                    second_point: PointNode) -> None:
    assert equivalence(not first_point == second_point,
                       first_point != second_point)
