from reprit.base import generate_repr

from .bound import Bound


class LocalMinimum:
    __slots__ = 'left_bound', 'right_bound', 'y', 'minimum_has_horizontal'

    def __init__(self,
                 left_bound: Bound,
                 right_bound: Bound,
                 y: float,
                 minimum_has_horizontal: bool) -> None:
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.y = y
        self.minimum_has_horizontal = minimum_has_horizontal

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'LocalMinimum') -> bool:
        return (self.left_bound == other.left_bound
                and self.right_bound == other.right_bound
                and self.y == other.y
                and self.minimum_has_horizontal is other.minimum_has_horizontal
                if isinstance(other, LocalMinimum)
                else NotImplemented)
