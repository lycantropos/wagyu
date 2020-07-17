from typing import (List,
                    Optional)

from _wagyu import (Bound,
                    Edge,
                    EdgeSide,
                    Point,
                    PolygonKind,
                    Ring)
from hypothesis import given

from . import strategies


@given(strategies.edges_lists, strategies.sizes, strategies.sizes, 
       strategies.points, strategies.maybe_rings, strategies.floats, 
       strategies.sizes, strategies.integers_32, strategies.integers_32, 
       strategies.trits, strategies.polygons_kinds, strategies.edges_sides)
def test_basic(edges: List[Edge],
               current_edge_index: int,
               next_edge_index: int,
               last_point: Point,
               ring: Optional[Ring],
               current_x: float,
               position: int,
               winding_count: int,
               opposite_winding_count: int,
               winding_delta: int,
               polygon_kind: PolygonKind,
               side: EdgeSide) -> None:
    result = Bound(edges, current_edge_index, next_edge_index, last_point,
                   ring, current_x, position, winding_count,
                   opposite_winding_count, winding_delta, polygon_kind, side)

    assert result.edges == edges
    assert result.current_edge_index == min(current_edge_index, len(edges))
    assert result.next_edge_index == min(next_edge_index, len(edges))
    assert result.last_point == last_point
    assert result.ring == ring
    assert result.maximum_bound is None
    assert result.current_x == current_x
    assert result.position == position
    assert result.winding_count == winding_count
    assert result.opposite_winding_count == opposite_winding_count
    assert result.winding_delta == winding_delta
    assert result.polygon_kind == polygon_kind
    assert result.side == side
