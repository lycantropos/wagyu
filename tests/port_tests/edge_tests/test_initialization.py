from hypothesis import given

from wagyu.edge import Edge
from wagyu.point import Point
from . import strategies


@given(strategies.points, strategies.points)
def test_basic(start: Point, end: Point) -> None:
    result = Edge(start, end)

    start_lower_than_end = start.y < end.y
    assert result.bottom == (end if start_lower_than_end else start)
    assert result.top == (start if start_lower_than_end else end)
