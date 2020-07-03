from _wagyu import PointNode
from hypothesis import given

from wagyu.hints import Coordinate
from . import strategies


@given(strategies.coordinates, strategies.coordinates)
def test_basic(x: Coordinate, y: Coordinate) -> None:
    result = PointNode(x, y)

    assert result.x == x
    assert result.y == y
