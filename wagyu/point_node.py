from typing import Tuple

from reprit.base import generate_repr

from .box import Box
from .hints import Coordinate
from .point import Point


class PointNode:
    __slots__ = 'x', 'y', 'prev', 'next'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        self.x = x
        self.y = y
        self.prev = self  # type: PointNode
        self.next = self  # type: PointNode

    def __eq__(self, other: 'PointNode') -> bool:
        return (self.x == other.x and self.y == other.y
                if isinstance(other, PointNode)
                else NotImplemented)

    __repr__ = generate_repr(__init__)

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
