import math

from reprit.base import generate_repr

from .point import Point


class Edge:
    __slots__ = 'top', 'bottom', 'slope'

    def __init__(self, top: Point, bottom: Point) -> None:
        self.top, self.bottom = ((top, bottom)
                                 if top.y < bottom.y
                                 else (bottom, top))
        dy = self.top.y - self.bottom.y
        self.slope = (self.top.x - self.bottom.x) / dy if dy else math.inf

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Edge') -> bool:
        return (self.top == other.top and self.bottom == other.bottom
                if isinstance(other, Edge)
                else NotImplemented)
