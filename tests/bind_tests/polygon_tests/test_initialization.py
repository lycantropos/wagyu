from typing import List

from _wagyu import (LinearRing,
                    Polygon)
from hypothesis import given

from . import strategies


@given(strategies.linear_rings_lists)
def test_basic(linear_rings: List[LinearRing]) -> None:
    result = Polygon(linear_rings)

    assert list(result) == linear_rings
