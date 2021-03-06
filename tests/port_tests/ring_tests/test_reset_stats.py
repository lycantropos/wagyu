from hypothesis import given

from wagyu.ring import (Box,
                        Point,
                        Ring)
from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    result = ring.reset_stats()

    assert result is None
    assert ring.box == Box(Point(0, 0), Point(0, 0))
