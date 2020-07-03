import copy

from _wagyu import LinearRing
from hypothesis import given

from . import strategies


@given(strategies.linear_rings)
def test_shallow(linear_ring: LinearRing) -> None:
    result = copy.copy(linear_ring)

    assert result is not linear_ring
    assert result == linear_ring


@given(strategies.linear_rings)
def test_deep(linear_ring: LinearRing) -> None:
    result = copy.deepcopy(linear_ring)

    assert result is not linear_ring
    assert result == linear_ring
