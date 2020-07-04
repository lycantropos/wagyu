import math
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .box import Box
from .point import Point
from .point_node import PointNode


class Ring:
    __slots__ = ('index', 'children', 'node', 'bottom_node', 'corrected',
                 'box', '_area', '_size', '_is_hole')

    def __init__(self,
                 index: int = 0,
                 children: Optional[List['Ring']] = None,
                 node: Optional[PointNode] = None,
                 bottom_node: Optional[PointNode] = None,
                 corrected: bool = False) -> None:
        self.index = index
        self.children = children
        self.node = node
        self.bottom_node = bottom_node
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
    def is_hole(self) -> bool:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._is_hole

    @property
    def size(self) -> int:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._size

    def recalculate_stats(self) -> None:
        if self.node is not None:
            self._area, self._size, self.box = self.node.stats
            self._is_hole = self._area <= 0.0

    def set_stats(self, area: float, size: int, box: Box) -> None:
        self._area, self._size, self.box, self._is_hole = (area, size, box,
                                                           area <= 0.0)

    def reset_stats(self) -> None:
        self._area = math.nan
        self._size = 0
        self.box.minimum.x = self.box.minimum.y = 0
        self.box.maximum.x = self.box.maximum.y = 0
        self._is_hole = False
