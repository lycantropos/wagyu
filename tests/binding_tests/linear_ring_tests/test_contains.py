from _wagyu import LinearRing
from hypothesis import given

from . import strategies


@given(strategies.linear_rings)
def test_self(linear_ring: LinearRing) -> None:
    assert all(element in linear_ring for element in linear_ring)
