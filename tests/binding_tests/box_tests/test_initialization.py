from _wagyu import (Box,
                    Point)
from hypothesis import given

from . import strategies


@given(strategies.points, strategies.points)
def test_basic(minimum: Point, maximum: Point) -> None:
    result = Box(minimum, maximum)

    assert result.minimum == minimum
    assert result.maximum == maximum
