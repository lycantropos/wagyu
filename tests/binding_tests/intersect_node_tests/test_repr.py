import sys

from _wagyu import IntersectNode
from hypothesis import given

from . import strategies


@given(strategies.intersect_nodes)
def test_basic(intersect_node: IntersectNode) -> None:
    result = repr(intersect_node)

    assert result.startswith(IntersectNode.__module__)
    assert IntersectNode.__qualname__ in result


@given(strategies.intersect_nodes)
def test_round_trip(intersect_node: IntersectNode) -> None:
    result = repr(intersect_node)

    assert eval(result, sys.modules) == intersect_node
