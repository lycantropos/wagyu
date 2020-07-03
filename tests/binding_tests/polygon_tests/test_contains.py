from _wagyu import Polygon
from hypothesis import given

from . import strategies


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert all(element in polygon for element in polygon)
