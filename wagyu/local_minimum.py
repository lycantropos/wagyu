from collections import abc
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .bound import (Bound,
                    create_bound_towards_maximum,
                    create_bound_towards_minimum)
from .edge import Edge
from .enums import (EdgeSide,
                    PolygonKind)
from .hints import Coordinate
from .linear_ring import LinearRing
from .utils import rotate_sequence


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

    def __lt__(self, other: 'LocalMinimum') -> bool:
        return ((self.y, self.minimum_has_horizontal)
                < (other.y, other.minimum_has_horizontal)
                if isinstance(other, LocalMinimum)
                else NotImplemented)

    def initialize(self) -> None:
        left_bound = self.left_bound
        if left_bound.edges:
            left_bound.current_edge_index = 0
            left_bound.next_edge_index = 1
            left_bound.current_x = float(left_bound.current_edge.bottom.x)
            left_bound.winding_count = left_bound.opposite_winding_count = 0
            left_bound.side = EdgeSide.LEFT
            left_bound.ring = None
        right_bound = self.right_bound
        if right_bound.edges:
            right_bound.current_edge_index = 0
            right_bound.next_edge_index = 1
            right_bound.current_x = float(right_bound.current_edge.bottom.x)
            right_bound.winding_count = right_bound.opposite_winding_count = 0
            right_bound.side = EdgeSide.RIGHT
            right_bound.ring = None


class LocalMinimumList(abc.MutableSequence):
    __slots__ = 'values',

    def __init__(self, *values: LocalMinimum) -> None:
        self.values = list(values)

    __repr__ = generate_repr(__init__)

    def __delitem__(self, index: int) -> None:
        del self.values[index]

    def __eq__(self, other: 'LocalMinimumList') -> bool:
        return (self.values == other.values
                if isinstance(other, LocalMinimumList)
                else NotImplemented)

    def __getitem__(self, index: int) -> LocalMinimum:
        return self.values[index]

    def __len__(self) -> int:
        return len(self.values)

    def __setitem__(self, index: int, value: LocalMinimum) -> None:
        self.values[index] = value

    @property
    def scanbeams(self) -> List[Coordinate]:
        return sorted(value.y for value in self.values)

    def add_linear_ring(self,
                        linear_ring: LinearRing,
                        polygon_kind: PolygonKind) -> bool:
        edges = linear_ring.edges
        if not edges:
            return False
        edges = to_edges_starting_on_local_maximum(edges)
        first_minimum = last_maximum = None  # type: Optional[Bound]
        while edges:
            to_minimum = create_bound_towards_minimum(edges)
            if not edges:
                raise RuntimeError('Edges is empty '
                                   'after only creating a single bound.')
            to_maximum = create_bound_towards_maximum(edges)
            to_minimum.fix_horizontals()
            to_maximum.fix_horizontals()
            maximum_edges = to_maximum.edges
            minimum_edges = to_minimum.edges
            try:
                max_non_horizontal_index = to_first_non_horizontal_index(
                        maximum_edges)
                min_non_horizontal_index = to_first_non_horizontal_index(
                        minimum_edges)
            except StopIteration as error:
                raise RuntimeError('should not have a horizontal only bound '
                                   'for a ring') from error
            minimum_has_horizontal = (max_non_horizontal_index > 0
                                      or min_non_horizontal_index > 0)
            if minimum_has_horizontal:
                if (maximum_edges[max_non_horizontal_index].bottom.x
                        > minimum_edges[min_non_horizontal_index].bottom.x):
                    minimum_is_left = True
                    to_minimum.move_horizontals(to_maximum)
                else:
                    minimum_is_left = False
                    to_maximum.move_horizontals(to_minimum)
            else:
                minimum_is_left = (
                        maximum_edges[max_non_horizontal_index].slope
                        <= minimum_edges[min_non_horizontal_index].slope)
            min_front = minimum_edges[0]
            if last_maximum:
                to_minimum.maximum_bound = last_maximum
            to_minimum.polygon_kind = to_maximum.polygon_kind = polygon_kind
            if not minimum_is_left:
                to_minimum.side = EdgeSide.RIGHT
                to_maximum.side = EdgeSide.LEFT
                to_minimum.winding_delta = -1
                to_maximum.winding_delta = 1
                minimum = LocalMinimum(to_maximum, to_minimum,
                                       min_front.bottom.y,
                                       minimum_has_horizontal)
                if last_maximum is None:
                    first_minimum = minimum.right_bound
                else:
                    last_maximum.maximum_bound = minimum.right_bound
                last_maximum = minimum.left_bound
            else:
                to_minimum.side = EdgeSide.LEFT
                to_maximum.side = EdgeSide.RIGHT
                to_minimum.winding_delta = -1
                to_maximum.winding_delta = 1
                minimum = LocalMinimum(to_minimum, to_maximum,
                                       min_front.bottom.y,
                                       minimum_has_horizontal)
                if last_maximum is None:
                    first_minimum = minimum.left_bound
                else:
                    last_maximum.maximum_bound = minimum.left_bound
                last_maximum = minimum.right_bound
            self.values.append(minimum)
        last_maximum.maximum_bound = first_minimum
        first_minimum.maximum_bound = last_maximum
        return True

    def insert(self, index: int, value: LocalMinimum) -> None:
        self.insert(index, value)


def to_edges_starting_on_local_maximum(edges: List[Edge]) -> List[Edge]:
    return (rotate_sequence(edges, to_local_maximum_index(edges))
            if len(edges) > 2
            else edges)


def to_local_maximum_index(edges: List[Edge]) -> int:
    prev_edge = edges[-1]
    prev_edge_is_horizontal = prev_edge.is_horizontal
    y_decreasing_before_last_horizontal = False
    for index, edge in enumerate(edges):
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
    else:
        index = len(edges)
    return index


def to_first_non_horizontal_index(edges: List[Edge]) -> int:
    return next(index
                for index, edge in enumerate(edges)
                if not edge.is_horizontal)
