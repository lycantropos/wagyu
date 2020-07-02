from typing import (List,
                    Optional)

from _wagyu import (PointNode,
                    Ring)
from hypothesis import given

from . import strategies


@given(strategies.sizes, strategies.maybe_rings_lists,
       strategies.maybe_points_nodes, strategies.maybe_points_nodes,
       strategies.booleans)
def test_basic(index: int,
               children: List[Optional[Ring]],
               node: Optional[PointNode],
               bottom_node: Optional[PointNode],
               corrected: bool) -> None:
    result = Ring(index, children, node, bottom_node, corrected)

    assert result.index == index
    assert result.children == children
    assert result.node == node
    assert result.bottom_node == bottom_node
    assert result.corrected is corrected
