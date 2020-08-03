from typing import (Iterator,
                    List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from .box import Box
from .edge import Edge
from .enums import PointInPolygonResult
from .hints import Coordinate
from .point import Point
from .utils import (are_floats_almost_equal,
                    are_floats_greater_than_or_equal,
                    is_float_almost_zero)


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


def point_in_polygon(pt: Point, op: PointNode) -> PointInPolygonResult:
    result = PointInPolygonResult.OUTSIDE
    start_op = op
    while True:
        if op.next.y == pt.y and (op.next.x == pt.x or op.y == pt.y
                                  and ((op.next.x > pt.x) is (op.x < pt.x))):
            return PointInPolygonResult.ON
        if (op.y < pt.y) is not (op.next.y < pt.y):
            if op.x >= pt.x:
                if op.next.x > pt.x:
                    # switch between point outside polygon
                    # and point inside polygon
                    result = (PointInPolygonResult.INSIDE
                              if result is PointInPolygonResult.OUTSIDE
                              else PointInPolygonResult.OUTSIDE)
                else:
                    d = ((op.x - pt.x) * (op.next.y - pt.y)
                         - (op.next.x - pt.x) * (op.y - pt.y))
                    if is_float_almost_zero(d):
                        return PointInPolygonResult.ON
                    if (d > 0) is (op.next.y > op.y):
                        result = (PointInPolygonResult.INSIDE
                                  if result is PointInPolygonResult.OUTSIDE
                                  else PointInPolygonResult.OUTSIDE)
            else:
                if op.next.x > pt.x:
                    d = ((op.x - pt.x) * (op.next.y - pt.y)
                         - (op.next.x - pt.x) * (op.y - pt.y))
                    if is_float_almost_zero(d):
                        return PointInPolygonResult.ON
                    if (d > 0) is (op.next.y > op.y):
                        result = (PointInPolygonResult.INSIDE
                                  if result is PointInPolygonResult.OUTSIDE
                                  else PointInPolygonResult.OUTSIDE)
        op = op.next
        if op is start_op:
            break
    return result


def inside_or_outside_special(first_polygon: PointNode,
                              other_polygon: PointNode
                              ) -> PointInPolygonResult:
    # we are going to loop through all the points of the original triangle,
    # the goal is to find a convex edge that with its next and previous
    # forms a triangle with its centroid that is within the first ring,
    # then we will check the other polygon to see if it is within this polygon
    cursor = first_polygon
    while True:
        if is_convex(cursor):
            centroid = points_centroid(cursor)
            if (point_in_polygon(centroid, first_polygon)
                    is PointInPolygonResult.INSIDE):
                return point_in_polygon(centroid, other_polygon)
        cursor = cursor.next
        if cursor is first_polygon:
            break
    raise RuntimeError('Could not find a point within the polygon to test')


def is_convex(node: PointNode) -> bool:
    area = node.ring.area
    prev_node = node.prev
    next_node = node.next
    delta_x = node.x - prev_node.x
    delta_y = node.y - prev_node.y
    next_delta_x = next_node.x - node.x
    next_delta_y = next_node.y - node.y
    cross = delta_x * next_delta_y - next_delta_x * delta_y
    return cross < 0 < area or cross > 0 > area


def points_centroid(node: PointNode) -> Point:
    prev_node = node.prev
    next_node = node.next
    return Point((prev_node.x + node.x + next_node.x) / 3,
                 (prev_node.y + node.y + next_node.y) / 3)
