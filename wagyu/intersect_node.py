from reprit.base import generate_repr

from .bound import Bound
from .point import Point


class IntersectNode:
    __slots__ = 'first_bound', 'second_bound', 'point'

    def __init__(self,
                 first_bound: Bound,
                 second_bound: Bound,
                 point: Point) -> None:
        self.first_bound = first_bound
        self.second_bound = second_bound
        self.point = point

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'IntersectNode') -> bool:
        return (self.first_bound == other.first_bound
                and self.second_bound == other.second_bound
                and self.point == other.point
                if isinstance(other, IntersectNode)
                else NotImplemented)
