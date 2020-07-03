from reprit import seekers
from reprit.base import generate_repr

from .point import Point


class Box:
    __slots__ = 'min', 'max'

    def __init__(self, min_: Point, max_: Point) -> None:
        self.min = min_
        self.max = max_

    __repr__ = generate_repr(__init__,
                             field_seeker=seekers.complex_)

    def __eq__(self, other: 'Box') -> bool:
        return (self.min == other.min and self.max == other.max
                if isinstance(other, Box)
                else NotImplemented)
