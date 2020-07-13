from decimal import (ROUND_HALF_UP,
                     Decimal)

from reprit.base import generate_repr

from wagyu.hints import Coordinate


class Point:
    __slots__ = 'x', 'y'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        self.x = x
        self.y = y

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Point') -> bool:
        return (self.x == other.x and self.y == other.y
                if isinstance(other, Point)
                else NotImplemented)

    def round(self) -> 'Point':
        return Point(round_up(self.x), round_up(self.y))


def round_up(value: Coordinate) -> Coordinate:
    return int(Decimal(value).quantize(1, ROUND_HALF_UP))
