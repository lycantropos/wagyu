from typing import List

from _wagyu import (LinearRing,
                    Point)
from hypothesis import given

from . import strategies


@given(strategies.linear_rings_points)
def test_basic(points: List[Point]) -> None:
    result = LinearRing(points)

    assert list(result) == points
