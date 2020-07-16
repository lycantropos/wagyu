from _wagyu import (Bound,
                    IntersectNode,
                    Point)
from hypothesis import given

from . import strategies


@given(strategies.bounds, strategies.bounds, strategies.points)
def test_basic(first_bound: Bound,
               second_bound: Bound,
               point: Point) -> None:
    result = IntersectNode(first_bound, second_bound, point)

    assert result.first_bound == first_bound
    assert result.second_bound == second_bound
    assert result.point == point
