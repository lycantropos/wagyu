import copy

from _wagyu import Multipolygon
from hypothesis import given

from . import strategies


@given(strategies.multipolygons)
def test_shallow(multipolygon: Multipolygon) -> None:
    result = copy.copy(multipolygon)

    assert result is not multipolygon
    assert result == multipolygon


@given(strategies.multipolygons)
def test_deep(multipolygon: Multipolygon) -> None:
    result = copy.deepcopy(multipolygon)

    assert result is not multipolygon
    assert result == multipolygon
