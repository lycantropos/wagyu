from _wagyu import Multipolygon
from hypothesis import given

from . import strategies


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert all(element in multipolygon for element in multipolygon)
