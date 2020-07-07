from collections import abc
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .bound import Bound
from .edge import Edge
from .enums import (EdgeSide,
                    PolygonKind)
from .linear_ring import LinearRing


class LocalMinimum:
    __slots__ = 'left_bound', 'right_bound', 'y', 'minimum_has_horizontal'

    def __init__(self,
                 left_bound: Bound,
                 right_bound: Bound,
                 y: float,
                 minimum_has_horizontal: bool) -> None:
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.y = y
        self.minimum_has_horizontal = minimum_has_horizontal

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'LocalMinimum') -> bool:
        return (self.left_bound == other.left_bound
                and self.right_bound == other.right_bound
                and self.y == other.y
                and self.minimum_has_horizontal is other.minimum_has_horizontal
                if isinstance(other, LocalMinimum)
                else NotImplemented)


class LocalMinimumList(abc.Sequence):
    __slots__ = 'values',

    def __init__(self, *values: LocalMinimum) -> None:
        self.values = list(values)

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'LocalMinimumList'):
        return (self.values == other.values
                if isinstance(other, LocalMinimumList)
                else NotImplemented)

    def __getitem__(self, index: int) -> LocalMinimum:
        return self.values[index]

    def __len__(self) -> int:
        return len(self.values)

    def add_linear_ring(self,
                        ring: LinearRing,
                        polygon_kind: PolygonKind) -> bool:
        edges = ring.edges
        if not edges:
            return False
        start_list_on_local_maximum(edges)
        first_minimum = last_maximum = None  # type: Optional[Bound]
        while edges:
            lm_minimum_has_horizontal = False
            to_minimum = create_bound_towards_minimum(edges)
            if not edges:
                raise RuntimeError('Edges is empty '
                                   'after only creating a single bound.')
            to_maximum = create_bound_towards_maximum(edges)
            fix_horizontals(to_minimum)
            fix_horizontals(to_maximum)
            max_non_horizontal_index = 0
            minimum_is_left = True
            maximum_edges = to_maximum.edges
            while (max_non_horizontal_index < len(maximum_edges)
                   and maximum_edges[max_non_horizontal_index].is_horizontal):
                lm_minimum_has_horizontal = True
                max_non_horizontal_index += 1
            min_non_horizontal_index = 0
            minimum_edges = to_minimum.edges
            while (min_non_horizontal_index < len(minimum_edges)
                   and minimum_edges[min_non_horizontal_index].is_horizontal):
                lm_minimum_has_horizontal = True
                min_non_horizontal_index += 1
            if (max_non_horizontal_index == len(maximum_edges)
                    or min_non_horizontal_index == len(minimum_edges)):
                raise RuntimeError('should not have a horizontal only bound '
                                   'for a ring')
            if lm_minimum_has_horizontal:
                if (maximum_edges[max_non_horizontal_index].bottom.x
                        > minimum_edges[min_non_horizontal_index].bottom.x):
                    minimum_is_left = True
                    move_horizontals_on_left_to_right(to_minimum, to_maximum)
                else:
                    minimum_is_left = False
                    move_horizontals_on_left_to_right(to_maximum, to_minimum)
            else:
                if (maximum_edges[max_non_horizontal_index].slope
                        > minimum_edges[min_non_horizontal_index].slope):
                    minimum_is_left = False
                else:
                    minimum_is_left = True
            assert minimum_edges
            assert maximum_edges
            min_front = minimum_edges[0]
            if last_maximum:
                to_minimum.maximum_bound = last_maximum
            to_minimum.polygon_kind = to_maximum.polygon_kind = polygon_kind
            if not minimum_is_left:
                to_minimum.side = EdgeSide.RIGHT
                to_maximum.side = EdgeSide.LEFT
                to_minimum.winding_delta = -1
                to_maximum.winding_delta = 1
                self.values.append(LocalMinimum(to_maximum, to_minimum,
                                                min_front.bottom.y,
                                                lm_minimum_has_horizontal))
                if last_maximum is None:
                    first_minimum = self[-1].right_bound
                else:
                    last_maximum.maximum_bound = self[-1].right_bound
                last_maximum = self[-1].left_bound
            else:
                to_minimum.side = EdgeSide.LEFT
                to_maximum.side = EdgeSide.RIGHT
                to_minimum.winding_delta = -1
                to_maximum.winding_delta = 1
                self.values.append(LocalMinimum(to_minimum, to_maximum,
                                                min_front.bottom.y,
                                                lm_minimum_has_horizontal))
                if last_maximum is None:
                    first_minimum = self[-1].left_bound
                else:
                    last_maximum.maximum_bound = self[-1].left_bound
                last_maximum = self[-1].right_bound
        last_maximum.maximum_bound = first_minimum
        first_minimum.maximum_bound = last_maximum
        return True


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


def start_list_on_local_maximum(edges: List[Edge]) -> None:
    if len(edges) <= 2:
        return
    prev_edge_index = len(edges) - 1
    prev_edge = edges[prev_edge_index]
    prev_edge_is_horizontal = prev_edge.is_horizontal
    index = 0
    y_decreasing_before_last_horizontal = False
    while index < len(edges):
        edge = edges[index]
        edge_is_horizontal = edge.is_horizontal
        if (not prev_edge_is_horizontal and not edge_is_horizontal
                and edge.top == prev_edge.top):
            break
        if not edge_is_horizontal and prev_edge_is_horizontal:
            if (y_decreasing_before_last_horizontal
                    and (edge.top == prev_edge.bottom
                         or edge.top == prev_edge.top)):
                break
        elif (not y_decreasing_before_last_horizontal
              and not prev_edge_is_horizontal and edge_is_horizontal
              and (prev_edge.top == edge.top or prev_edge.top == edge.bottom)):
            y_decreasing_before_last_horizontal = True
        prev_edge, prev_edge_is_horizontal = edge, edge_is_horizontal
        index += 1
    edges[:] = edges[index:] + edges[:index]


def fix_horizontals(bound: Bound) -> None:
    edge_index = 0
    next_index = 1
    edges = bound.edges
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


def move_horizontals_on_left_to_right(left_bound: Bound,
                                      right_bound: Bound) -> None:
    index = 0
    left_edges = left_bound.edges
    while index < len(left_edges):
        edge = left_edges[index]
        if not edge.is_horizontal:
            break
        edge.reverse_horizontal()
        index += 1
    if not index:
        return
    right_edges = right_bound.edges
    right_edges.extend(reversed(left_edges[:index]))
    del left_edges[:index]
    right_edges[:] = right_edges[-index:] + right_edges[:-index]
