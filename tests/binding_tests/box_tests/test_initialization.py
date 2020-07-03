from _wagyu import (Box,
                    Point)
from hypothesis import given

from . import strategies


@given(strategies.points, strategies.points)
def test_basic(min_: Point, max_: Point) -> None:
    result = Box(min_, max_)

    assert result.min == min_
    assert result.max == max_
