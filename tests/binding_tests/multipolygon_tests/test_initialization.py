from typing import List

from _wagyu import (Multipolygon,
                    Polygon)
from hypothesis import given

from . import strategies


@given(strategies.polygons_lists)
def test_basic(polygons: List[Polygon]) -> None:
    result = Multipolygon(polygons)

    assert list(result) == polygons
