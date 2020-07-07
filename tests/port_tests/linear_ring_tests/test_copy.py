import copy

from hypothesis import given

from wagyu.linear_ring import LinearRing
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
