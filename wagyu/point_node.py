from typing import (Iterator,
                    List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from .box import Box
from .hints import Coordinate
from .point import Point


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

    def __iter__(self) -> Iterator[Point]:
        cursor = self
        while True:
            yield Point(cursor.x, cursor.y)
            cursor = cursor.next
            if cursor is self:
                break

    @classmethod
    def from_point(cls, point: Point) -> 'PointNode':
        return PointNode(point.x, point.y)

    @classmethod
    def from_points(cls, points: List[Point]) -> 'PointNode':
        points = reversed(points)
        result = cls.from_point(next(points))
        for point in points:
            node = cls.from_point(point)
            node.place_before(result)
            result = node
        return result


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

    def reverse(self) -> None:
        cursor = self
        while True:
            cursor, cursor.next, cursor.prev = (cursor.next, cursor.prev,
                                                cursor.next)
            if cursor is self:
                break

    def place_before(self, other: 'PointNode') -> None:
        self.next, self.prev = other, other.prev
        self.prev.next = other.prev = self


def maybe_point_node_to_points(node: Optional[PointNode]) -> List[Point]:
    return [] if node is None else list(node)
