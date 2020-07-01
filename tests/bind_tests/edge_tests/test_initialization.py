from _wagyu import (Edge,
                    Point)
from hypothesis import given

from . import strategies


@given(strategies.points, strategies.points)
def test_basic(start: Point, end: Point) -> None:
    result = Edge(start, end)

    start_lower_than_end = start.y < end.y
    assert result.bottom == (end if start_lower_than_end else start)
    assert result.top == (start if start_lower_than_end else end)
