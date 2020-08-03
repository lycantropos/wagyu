from typing import (Iterator,
                    List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from .box import Box
from .edge import Edge
from .hints import Coordinate
from .point import Point
from .utils import (are_floats_almost_equal,
                    are_floats_greater_than_or_equal)


class PointNode:
    __slots__ = 'x', 'y', 'prev', 'next', 'ring'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        from .ring import Ring
        self.x = x
        self.y = y
        self.prev = self  # type: PointNode
        self.next = self  # type: PointNode
        self.ring = None  # type: Optional[Ring]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'PointNode') -> bool:
        return (self.x == other.x and self.y == other.y
                if isinstance(other, (Point, PointNode))
                else NotImplemented)

    def __iter__(self) -> Iterator['PointNode']:
        cursor = self
        while True:
            yield cursor
            cursor = cursor.next
            if cursor is self:
                break

    def __lt__(self, other: 'PointNode') -> bool:
        if self.y != other.y:
            return self.y < other.y
        elif other.x != self.x:
            return self.x > other.x
        else:
            return self.ring.depth < other.ring.depth

    def __reversed__(self) -> Iterator['PointNode']:
        cursor = self
        while True:
            yield cursor
            cursor = cursor.prev
            if cursor is self:
                break

    @classmethod
    def from_point(cls, point: Point) -> 'PointNode':
        return cls(point.x, point.y)

    @property
    def bottom_node(self) -> 'PointNode':
        dups = None
        node = self
        cursor = node.next
        while cursor is not node:
            if cursor.y > node.y:
                node = cursor
                dups = None
            elif cursor.y == node.y and cursor.x <= node.x:
                if cursor.x < node.x:
                    dups = None
                    node = cursor
                else:
                    if cursor.next is not node and cursor.prev is node:
                        dups = cursor
            cursor = cursor.next
        if dups is not None:
            # there appears to be at least 2 vertices at bottom_point so ...
            while dups is not cursor:
                if not cursor.is_bottom_to(dups):
                    node = dups
                dups = dups.next
                while dups != node:
                    dups = dups.next
        return node

    @property
    def stats(self) -> Tuple[float, int, Box]:
        area = size = 0
        min_x = max_x = self.x
        min_y = max_y = self.y
        cursor = self
        while True:
            size += 1
            if cursor.x > max_x:
                max_x = cursor.x
            elif cursor.x < min_x:
                min_x = cursor.x
            if cursor.y > max_y:
                max_y = cursor.y
            elif cursor.y < min_y:
                min_y = cursor.y
            area += (cursor.prev.x + cursor.x) * (cursor.prev.y - cursor.y)
            cursor = cursor.next
            if cursor is self:
                break
        return area / 2, size, Box(Point(min_x, min_y), Point(max_x, max_y))

    def is_bottom_to(self, other: 'PointNode') -> bool:
        node = self.prev
        while node == self and node is not self:
            node = node.prev
        dx1p = abs(get_points_slope(self, node))
        node = self.next
        while node == self and node is not self:
            node = node.next
        dx1n = abs(get_points_slope(self, node))
        node = other.prev
        while node == other and node is not other:
            node = node.prev
        dx2p = abs(get_points_slope(other, node))
        node = other.next
        while node == other and node is not other:
            node = node.next
        dx2n = abs(get_points_slope(other, node))
        if (are_floats_almost_equal(max(dx1p, dx1n), max(dx2p, dx2n))
                and are_floats_almost_equal(min(dx1p, dx1n), min(dx2p, dx2n))):
            area, *_ = self.stats
            return area > 0.0  # if otherwise identical use orientation
        else:
            return ((are_floats_greater_than_or_equal(dx1p, dx2p)
                     and are_floats_greater_than_or_equal(dx1p, dx2n))
                    or (are_floats_greater_than_or_equal(dx1n, dx2p)
                        and are_floats_greater_than_or_equal(dx1n, dx2n)))

    def reverse(self) -> None:
        for node in self:
            node.next, node.prev = node.prev, node.next

    def place_before(self, other: 'PointNode') -> None:
        self.next, self.prev = other, other.prev
        self.prev.next = other.prev = self


def get_points_slope(left: PointNode, right: PointNode) -> float:
    return Edge(point_node_to_point(left), point_node_to_point(right)).slope


def point_node_to_point(node: PointNode) -> Point:
    return Point(node.x, node.y)


def maybe_point_node_to_points(node: Optional[PointNode]) -> List[Point]:
    return [] if node is None else [Point(sub_node.x, sub_node.y)
                                    for sub_node in node]


def node_key(node: PointNode) -> Tuple[Coordinate, Coordinate]:
    return -node.y, node.x
