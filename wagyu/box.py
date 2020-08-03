from reprit.base import generate_repr

from .point import Point


class Box:
    __slots__ = 'minimum', 'maximum'

    def __init__(self, minimum: Point, maximum: Point) -> None:
        self.minimum = minimum
        self.maximum = maximum

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Box') -> bool:
        return (self.minimum == other.minimum and self.maximum == other.maximum
                if isinstance(other, Box)
                else NotImplemented)

    def inside_of(self, other: 'Box') -> bool:
        return (other.minimum.x <= self.minimum.x
                and other.minimum.y <= self.minimum.y
                and other.maximum.x >= self.maximum.x
                and other.maximum.y >= self.maximum.y)
