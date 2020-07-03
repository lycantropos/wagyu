import sys

from _wagyu import Multipolygon
from hypothesis import given

from . import strategies


@given(strategies.multipolygons)
def test_basic(multipolygon: Multipolygon) -> None:
    result = repr(multipolygon)

    assert result.startswith(Multipolygon.__module__)
    assert Multipolygon.__qualname__ in result


@given(strategies.multipolygons)
def test_round_trip(multipolygon: Multipolygon) -> None:
    result = repr(multipolygon)

    assert eval(result, sys.modules) == multipolygon
