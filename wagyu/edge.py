import math
from typing import Optional

from reprit.base import generate_repr

from .hints import Coordinate
from .point import Point


class Edge:
    __slots__ = 'top', 'bottom', 'slope'

    def __init__(self, bottom: Point, top: Point) -> None:
        self.bottom, self.top = ((top, bottom)
                                 if bottom.y < top.y
                                 else (bottom, top))
        dy = self.top.y - self.bottom.y
        self.slope = (self.top.x - self.bottom.x) / dy if dy else math.inf

    __repr__ = generate_repr(__init__)

    def __and__(self, other: 'Edge') -> Optional[Point]:
        delta_x = self.top.x - self.bottom.x
        delta_y = self.top.y - self.bottom.y
        other_delta_x = other.top.x - other.bottom.x
        other_delta_y = other.top.y - other.bottom.y
        denominator = delta_x * other_delta_y - other_delta_x * delta_y
        if not denominator:
            return None
        s = ((-delta_y * (self.bottom.x - other.bottom.x)
              + delta_x * (self.bottom.y - other.bottom.y))
             / denominator)
        t = ((other_delta_x * (self.bottom.y - other.bottom.y)
              - other_delta_y * (self.bottom.x - other.bottom.x))
             / denominator)
        return (Point(self.bottom.x + (t * delta_x),
                      self.bottom.y + (t * delta_y))
                if 0. <= s <= 1. and 0. <= t <= 1.
                else None)

    def __eq__(self, other: 'Edge') -> bool:
        return (self.top == other.top and self.bottom == other.bottom
                if isinstance(other, Edge)
                else NotImplemented)

    @property
    def is_horizontal(self) -> bool:
        return math.isinf(self.slope)

    def get_current_x(self, current_y: Coordinate) -> Coordinate:
        return float(
                self.top.x
                if current_y == self.top.y
                else self.bottom.x + self.slope * (current_y - self.bottom.y))

    def reverse_horizontal(self) -> None:
        self.top, self.bottom = (Point(self.bottom.x, self.top.y),
                                 Point(self.top.x, self.bottom.y))
