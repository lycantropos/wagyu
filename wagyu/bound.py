from functools import partial
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .edge import (Edge,
                   are_edges_slopes_equal)
from .enums import (EdgeSide,
                    FillKind,
                    OperationKind,
                    PolygonKind)
from .hints import Coordinate
from .point import Point
from .ring import Ring
from .utils import (are_floats_almost_equal,
                    are_floats_greater_than,
                    are_floats_less_than,
                    find_if,
                    insort_unique)


class Bound:
    __slots__ = ('edges', '_current_edge_index', '_next_edge_index',
                 'last_point', 'ring', 'current_x', 'position',
                 'winding_count', 'opposite_winding_count', 'winding_delta',
                 'polygon_kind', 'side', 'maximum_bound')

    def __init__(self,
                 edges: Optional[List[Edge]] = None,
                 current_edge_index: Optional[int] = None,
                 next_edge_index: Optional[int] = None,
                 last_point: Optional[Point] = None,
                 ring: Optional[Ring] = None,
                 current_x: float = 0.,
                 position: int = 0,
                 winding_count: int = 0,
                 opposite_winding_count: int = 0,
                 winding_delta: int = 0,
                 polygon_kind: PolygonKind = PolygonKind.SUBJECT,
                 side: EdgeSide = EdgeSide.LEFT) -> None:
        self.edges = edges or []
        self._current_edge_index = (
            None
            if (current_edge_index is None
                or current_edge_index >= len(self.edges))
            else current_edge_index)
        self._next_edge_index = (None
                                 if (next_edge_index is None
                                     or next_edge_index >= len(self.edges))
                                 else next_edge_index)
        self.last_point = Point(0, 0) if last_point is None else last_point
        self.ring = ring
        self.current_x = current_x
        self.position = position
        self.winding_count = winding_count
        self.opposite_winding_count = opposite_winding_count
        self.winding_delta = winding_delta
        self.polygon_kind = polygon_kind
        self.side = side
        self.maximum_bound = None  # type: Optional[Bound]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Bound') -> bool:
        return (self.edges == other.edges
                and self.current_edge_index == other.current_edge_index
                and self.next_edge_index == other.next_edge_index
                and self.last_point == other.last_point
                and self.ring == other.ring
                and self.current_x == other.current_x
                and self.position == other.position
                and self.winding_count == other.winding_count
                and self.opposite_winding_count == other.opposite_winding_count
                and self.winding_delta == other.winding_delta
                and self.polygon_kind is other.polygon_kind
                and self.side is other.side
                if isinstance(other, Bound)
                else NotImplemented)

    @property
    def current_edge(self) -> Edge:
        return self.edges[self.current_edge_index]

    @property
    def next_edge(self) -> Edge:
        return self.edges[self.next_edge_index]

    @property
    def current_edge_index(self) -> int:
        return (len(self.edges)
                if self._current_edge_index is None
                else self._current_edge_index)

    @property
    def next_edge_index(self) -> int:
        return (len(self.edges)
                if self._next_edge_index is None
                else self._next_edge_index)

    @current_edge_index.setter
    def current_edge_index(self, value: int) -> None:
        self._current_edge_index = value if value < len(self.edges) else None

    @next_edge_index.setter
    def next_edge_index(self, value: int) -> None:
        self._next_edge_index = value if value < len(self.edges) else None

    def is_contributing(self,
                        operation_kind: OperationKind,
                        subject_fill_kind: FillKind,
                        clip_fill_kind: FillKind) -> bool:
        pft, pft2 = ((subject_fill_kind, clip_fill_kind)
                     if self.polygon_kind is PolygonKind.SUBJECT
                     else (clip_fill_kind, subject_fill_kind))
        if pft is FillKind.NON_ZERO:
            if abs(self.winding_count) != 1:
                return False
        elif pft is FillKind.POSITIVE:
            if self.winding_count != 1:
                return False
        elif pft is FillKind.NEGATIVE:
            if self.winding_count != -1:
                return False
        if operation_kind is OperationKind.INTERSECTION:
            if pft2 is FillKind.EVEN_ODD or pft2 is FillKind.NON_ZERO:
                return self.opposite_winding_count != 0
            elif pft2 is FillKind.POSITIVE:
                return self.opposite_winding_count > 0
            else:
                return self.opposite_winding_count < 0
        elif operation_kind is OperationKind.UNION:
            if pft2 is FillKind.EVEN_ODD or pft2 is FillKind.NON_ZERO:
                return self.opposite_winding_count == 0
            elif pft2 is FillKind.POSITIVE:
                return self.opposite_winding_count <= 0
            else:
                return self.opposite_winding_count >= 0
        elif operation_kind is OperationKind.DIFFERENCE:
            if self.polygon_kind is PolygonKind.SUBJECT:
                if pft2 is FillKind.EVEN_ODD or pft2 is FillKind.NON_ZERO:
                    return self.opposite_winding_count == 0
                elif pft2 is FillKind.POSITIVE:
                    return self.opposite_winding_count <= 0
                else:
                    return self.opposite_winding_count >= 0
            else:
                if pft2 is FillKind.EVEN_ODD or pft2 is FillKind.NON_ZERO:
                    return self.opposite_winding_count != 0
                elif pft2 is FillKind.POSITIVE:
                    return self.opposite_winding_count > 0
                else:
                    return self.opposite_winding_count < 0
        else:
            return True

    def is_even_odd_fill_kind(self,
                              subject_fill_kind: FillKind,
                              clip_fill_kind: FillKind) -> bool:
        if self.polygon_kind is PolygonKind.SUBJECT:
            return subject_fill_kind is FillKind.EVEN_ODD
        else:
            return clip_fill_kind is FillKind.EVEN_ODD

    def is_even_odd_alt_fill_kind(self,
                                  subject_fill_kind: FillKind,
                                  clip_fill_kind: FillKind) -> bool:
        if self.polygon_kind is PolygonKind.SUBJECT:
            return clip_fill_kind is FillKind.EVEN_ODD
        else:
            return subject_fill_kind is FillKind.EVEN_ODD

    def is_intermediate(self, y: Coordinate) -> bool:
        return (self.next_edge_index != len(self.edges)
                and self.current_edge.top.y == y)

    def is_maxima(self, y: Coordinate) -> bool:
        return (self.next_edge_index == len(self.edges)
                and self.current_edge.top.y == y)

    def fix_horizontals(self) -> None:
        edge_index = 0
        next_index = 1
        edges = self.edges
        if next_index == len(edges):
            return
        edge = edges[edge_index]
        if edge.is_horizontal and edges[next_index].bottom != edge.top:
            edge.reverse_horizontal()
        prev_edge = edge
        edge_index += 1
        while edge_index < len(edges):
            edge = edges[edge_index]
            if edge.is_horizontal and prev_edge.top != edge.bottom:
                edge.reverse_horizontal()
            prev_edge = edge
            edge_index += 1

    def move_horizontals(self, other: 'Bound') -> None:
        index = 0
        edges = self.edges
        while index < len(edges):
            edge = edges[index]
            if not edge.is_horizontal:
                break
            edge.reverse_horizontal()
            index += 1
        if not index:
            return
        other_edges = other.edges
        other_edges.extend(reversed(edges[:index]))
        del edges[:index]
        other_edges[:] = other_edges[-index:] + other_edges[:-index]

    def to_next_edge(self, scanbeams: List[Coordinate]) -> None:
        self.current_edge_index += 1
        if self.current_edge_index < len(self.edges):
            self.next_edge_index += 1
            self.current_x = self.current_edge.bottom.x
            if not self.current_edge.is_horizontal:
                insort_unique(scanbeams, self.current_edge.top.y)


def create_bound_towards_maximum(edges: List[Edge]) -> Bound:
    if len(edges) == 1:
        result = Bound(edges[:])
        edges.clear()
        return result
    next_edge_index = 0
    edge = edges[next_edge_index]
    next_edge_index += 1
    edge_is_horizontal = edge.is_horizontal
    y_decreasing_before_last_horizontal = False
    while next_edge_index < len(edges):
        next_edge = edges[next_edge_index]
        next_edge_is_horizontal = next_edge.is_horizontal
        if (not next_edge_is_horizontal and not edge_is_horizontal
                and edge.top == next_edge.top):
            break
        if not next_edge_is_horizontal and edge_is_horizontal:
            if (y_decreasing_before_last_horizontal
                    and (next_edge.top == edge.bottom
                         or next_edge.top == edge.top)):
                break
        elif (not y_decreasing_before_last_horizontal
              and not edge_is_horizontal and next_edge_is_horizontal
              and (edge.top == next_edge.top or edge.top == next_edge.bottom)):
            y_decreasing_before_last_horizontal = True
        edge, edge_is_horizontal = next_edge, next_edge_is_horizontal
        next_edge_index += 1
    if next_edge_index == len(edges):
        result = Bound(edges[:])
        edges.clear()
    else:
        result = Bound(edges[:next_edge_index])
        del edges[:next_edge_index]
    return result


def create_bound_towards_minimum(edges: List[Edge]) -> Bound:
    if len(edges) == 1:
        first_edge = edges[0]
        if first_edge.is_horizontal:
            first_edge.reverse_horizontal()
        result = Bound(edges[:])
        edges.clear()
        return result
    next_edge_index = 0
    edge = edges[next_edge_index]
    next_edge_index += 1
    edge_is_horizontal = edge.is_horizontal
    if edge_is_horizontal:
        edge.reverse_horizontal()
    y_increasing_before_last_horizontal = False
    while next_edge_index < len(edges):
        next_edge = edges[next_edge_index]
        next_edge_is_horizontal = next_edge.is_horizontal
        if (not next_edge_is_horizontal and not edge_is_horizontal
                and edge.bottom == next_edge.bottom):
            break
        if not next_edge_is_horizontal and edge_is_horizontal:
            if (y_increasing_before_last_horizontal
                    and (next_edge.bottom == edge.bottom
                         or next_edge.bottom == edge.top)):
                break
        elif (not y_increasing_before_last_horizontal
              and not edge_is_horizontal and next_edge_is_horizontal
              and (edge.bottom == next_edge.top
                   or edge.bottom == next_edge.bottom)):
            y_increasing_before_last_horizontal = True
        edge_is_horizontal, edge = next_edge_is_horizontal, next_edge
        if edge_is_horizontal:
            edge.reverse_horizontal()
        next_edge_index += 1
    if next_edge_index == len(edges):
        result = Bound(edges[:])
        edges.clear()
    else:
        result = Bound(edges[:next_edge_index])
        del edges[:next_edge_index]
    result.edges.reverse()
    return result


def bound_insert_location(left: Bound, right: Bound) -> bool:
    if are_floats_almost_equal(left.current_x, right.current_x):
        if left.current_edge.top.y > right.current_edge.top.y:
            return are_floats_less_than(float(left.current_edge.top.x),
                                        right.current_edge.get_current_x(
                                                left.current_edge.top.y))
        else:
            return are_floats_greater_than(float(right.current_edge.top.x),
                                           left.current_edge.get_current_x(
                                                   right.current_edge.top.y))
    else:
        return left.current_x < right.current_x


def insert_bound_into_abl(left: Bound,
                          right: Bound,
                          active_bounds: List[Bound]) -> int:
    index = find_if(partial(bound_insert_location, left),
                    active_bounds)
    active_bounds.insert(index, right)
    active_bounds.insert(index, left)
    return index


def intersection_compare(left: Bound, right: Bound) -> bool:
    return not (left.current_x > right.current_x and
                not are_edges_slopes_equal(left.current_edge,
                                           right.current_edge))


def set_winding_count(bound_index: int, active_bounds: List[Bound],
                      subject_fill_kind: FillKind, clip_fill_kind: FillKind
                      ) -> None:
    bound = active_bounds[bound_index]
    if not bound_index:
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = 0
        return
    # find the edge of the same polygon kind that immediately precedes 'edge'
    # in AEL
    reversed_bound_index = bound_index - 1
    while (reversed_bound_index >= 0
           and (active_bounds[reversed_bound_index].polygon_kind
                is not bound.polygon_kind)):
        reversed_bound_index -= 1
    if reversed_bound_index == -1:
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = 0
    elif bound.is_even_odd_fill_kind(subject_fill_kind, clip_fill_kind):
        # even-odd filling
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = (active_bounds[reversed_bound_index]
                                        .opposite_winding_count)
    else:
        # non-zero, positive or negative filling
        reversed_bound = active_bounds[reversed_bound_index]
        if reversed_bound.winding_count * reversed_bound.winding_delta < 0:
            # previous edge is 'decreasing' winding count toward zero
            # so we're outside the previous polygon
            if abs(reversed_bound.winding_count) > 1:
                # outside previous polygon but still inside another,
                # when reversing direction of previous polygon
                # use the same winding count
                if reversed_bound.winding_delta * bound.winding_delta < 0:
                    bound.winding_count = reversed_bound.winding_count
                else:
                    # otherwise continue to 'decrease' winding count
                    bound.winding_count = (reversed_bound.winding_count
                                           + bound.winding_delta)
            else:
                # now outside all polygons of same polygon kind
                # so set own winding count
                bound.winding_count = bound.winding_delta
        else:
            # previous edge is 'increasing' winding count away from zero
            # so we're inside the previous polygon
            if reversed_bound.winding_delta * bound.winding_delta < 0:
                # if wind direction is reversing previous
                # then use same winding count
                bound.winding_count = reversed_bound.winding_count
            else:
                # otherwise add to winding count
                bound.winding_count = (reversed_bound.winding_count
                                       + bound.winding_delta)
        bound.opposite_winding_count = reversed_bound.opposite_winding_count
    # update opposite winding count
    forward_bound_index = reversed_bound_index + 1
    if bound.is_even_odd_alt_fill_kind(subject_fill_kind, clip_fill_kind):
        # even-odd filling
        for forward_bound_index in range(forward_bound_index, bound_index):
            bound.opposite_winding_count = int(
                    not bound.opposite_winding_count)
    else:
        # non-zero, positive or negative filling
        for forward_bound_index in range(forward_bound_index, bound_index):
            bound.opposite_winding_count += (active_bounds[forward_bound_index]
                                             .winding_delta)
