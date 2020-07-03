from wagyu.point import Point
from hypothesis import given

from wagyu.hints import Coordinate
from . import strategies


@given(strategies.coordinates, strategies.coordinates)
def test_basic(x: Coordinate, y: Coordinate) -> None:
    result = Point(x, y)

    assert result.x == x
    assert result.y == y
