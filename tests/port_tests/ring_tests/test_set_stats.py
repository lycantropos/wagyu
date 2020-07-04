from hypothesis import given

from wagyu.ring import (Box,
                        Ring)
from . import strategies


@given(strategies.rings, strategies.floats, strategies.sizes, strategies.boxes)
def test_basic(ring: Ring, area: float, size: int, box: Box) -> None:
    result = ring.set_stats(area, size, box)

    assert result is None
    assert ring.area == area
    assert ring.size == size
    assert ring.box == box
