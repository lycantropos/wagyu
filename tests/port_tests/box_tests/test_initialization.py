from hypothesis import given

from wagyu.box import Box
from wagyu.point import Point
from . import strategies


@given(strategies.points, strategies.points)
def test_basic(min_: Point, max_: Point) -> None:
    result = Box(min_, max_)

    assert result.minimum == min_
    assert result.maximum == max_
