import sys

from _wagyu import LinearRing
from hypothesis import given

from . import strategies


@given(strategies.linear_rings)
def test_basic(linear_ring: LinearRing) -> None:
    result = repr(linear_ring)

    assert result.startswith(LinearRing.__module__)
    assert LinearRing.__qualname__ in result


@given(strategies.linear_rings)
def test_round_trip(linear_ring: LinearRing) -> None:
    result = repr(linear_ring)

    assert eval(result, sys.modules) == linear_ring
