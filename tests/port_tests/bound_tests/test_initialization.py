from typing import (List,
                    Optional)

from hypothesis import given

from wagyu.bound import Bound
from wagyu.edge import Edge
from wagyu.enums import (EdgeSide,
                         PolygonKind)
from wagyu.point import Point
from wagyu.ring import Ring
from . import strategies


@given(strategies.edges_lists, strategies.non_negative_integers,
       strategies.non_negative_integers, strategies.points,
       strategies.maybe_rings, strategies.floats,
       strategies.non_negative_integers, strategies.integers,
       strategies.integers, strategies.trits, strategies.polygon_kinds,
       strategies.edges_sides)
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
    assert result.polygon_kind is polygon_kind
    assert result.side is side
