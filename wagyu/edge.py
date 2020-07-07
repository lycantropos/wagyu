import math

from reprit.base import generate_repr

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

    def __eq__(self, other: 'Edge') -> bool:
        return (self.top == other.top and self.bottom == other.bottom
                if isinstance(other, Edge)
                else NotImplemented)

    @property
    def is_horizontal(self) -> bool:
        return math.isinf(self.slope)

    def reverse_horizontal(self) -> None:
        self.top.x, self.bottom.x = self.bottom.x, self.top.x
