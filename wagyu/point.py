from reprit.base import generate_repr

from .hints import Coordinate
from .utils import round_towards_max


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
        return Point(round_towards_max(self.x), round_towards_max(self.y))


def are_points_slopes_equal(first: Point, second: Point, third: Point) -> bool:
    return ((first.y - second.y) * (second.x - third.x)
            == (first.x - second.x) * (second.y - third.y))


def is_point_between_others(pt1: Point, pt2: Point, pt3: Point) -> bool:
    if pt1 == pt2 or pt2 == pt3 or pt1 == pt3:
        return False
    elif pt1.x != pt3.x:
        return (pt2.x > pt1.x) is (pt2.x < pt3.x)
    else:
        return (pt2.y > pt1.y) is (pt2.y < pt3.y)
