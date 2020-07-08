from typing import (List,
                    Optional)

from _wagyu import (Point,
                    PointNode,
                    Ring,
                    RingManager)
from hypothesis import given

from . import strategies


@given(strategies.maybe_rings_lists, strategies.maybe_points_nodes_lists,
       strategies.points_lists, strategies.points_nodes_lists,
       strategies.rings_lists, strategies.points_nodes_lists, strategies.sizes)
def test_basic(children: List[Optional[Ring]],
               all_nodes: List[Optional[PointNode]],
               hot_pixels: List[Point],
               nodes: List[PointNode],
               rings: List[Ring],
               storage: List[PointNode],
               index: int) -> None:
    result = RingManager(children, all_nodes, hot_pixels, nodes, rings,
                         storage, index)

    assert result.children == children
    assert result.all_nodes == all_nodes
    assert result.hot_pixels == hot_pixels
    assert result.nodes == nodes
    assert result.storage == storage
    assert result.rings == rings
    assert result.index == index
