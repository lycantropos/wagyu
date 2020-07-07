from typing import List

from hypothesis import given

from wagyu.linear_ring import LinearRing
from wagyu.point import Point
from . import strategies


@given(strategies.linear_rings_points)
def test_basic(points: List[Point]) -> None:
    result = LinearRing(points)

    assert list(result) == points
