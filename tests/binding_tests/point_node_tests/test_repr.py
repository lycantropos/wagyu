import sys

from _wagyu import PointNode
from hypothesis import given

from . import strategies


@given(strategies.points_nodes)
def test_basic(point_node: PointNode) -> None:
    result = repr(point_node)

    assert result.startswith(PointNode.__module__)
    assert PointNode.__qualname__ in result


@given(strategies.points_nodes)
def test_round_trip(point_node: PointNode) -> None:
    result = repr(point_node)

    assert eval(result, sys.modules) == point_node
