import math
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .box import Box
from .point import Point
from .point_node import (PointNode,
                         maybe_point_node_to_points)


class Ring:
    __slots__ = ('index', 'parent', 'children', 'node', 'bottom_node',
                 'corrected', 'box', '_area', '_size', '_is_hole')

    def __init__(self,
                 index: int = 0,
                 children: Optional[List[Optional['Ring']]] = None,
                 points: Optional[List[Point]] = None,
                 corrected: bool = False) -> None:
        self.index = index
        self.parent = None  # type: Optional[Ring]
        self.children = children or []
        self.node = None if not points else PointNode.from_points(points)
        self.bottom_node = None  # type: Optional[PointNode]
        self.corrected = corrected
        self.box = Box(Point(0, 0), Point(0, 0))  # type: Box
        self._area = math.nan  # type: float
        self._is_hole = False  # type: bool
        self._size = 0  # type: int

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Ring') -> bool:
        return (self.index == other.index
                and self.children == other.children
                and self.node == other.node
                and self.bottom_node == other.bottom_node
                and self.corrected is other.corrected
                if isinstance(other, Ring)
                else NotImplemented)

    @property
    def area(self) -> float:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._area

    @property
    def depth(self) -> int:
        result = 0
        cursor = self.parent
        while cursor is not None:
            result += 1
            cursor = cursor.parent
        return result

    @property
    def is_hole(self) -> bool:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._is_hole

    @property
    def points(self) -> List[Point]:
        return maybe_point_node_to_points(self.node)

    @property
    def bottom_points(self) -> List[Point]:
        return maybe_point_node_to_points(self.bottom_node)

    @property
    def size(self) -> int:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._size

    def recalculate_stats(self) -> None:
        if self.node is not None:
            self._area, self._size, self.box = self.node.stats
            self._is_hole = self._area <= 0.0

    def reset_stats(self) -> None:
        self._area = math.nan
        self._size = 0
        self.box.minimum.x = self.box.minimum.y = 0
        self.box.maximum.x = self.box.maximum.y = 0
        self._is_hole = False

    def set_stats(self, area: float, size: int, box: Box) -> None:
        self._area, self._size, self.box, self._is_hole = (area, size, box,
                                                           area <= 0.0)

    def update_points(self) -> None:
        for node in self.node:
            node.ring = self


def remove_from_children(ring: Ring, children: List[Optional[Ring]]) -> None:
    for index, candidate in enumerate(children):
        if candidate is ring:
            children[index] = None
            return


def set_to_children(r: Ring, children: List[Optional[Ring]]) -> None:
    for index, c in enumerate(children):
        if c is None:
            children[index] = r
            return
    children.append(r)
