from _wagyu import (Edge,
                    LinearRing)
from hypothesis import given

from . import strategies


@given(strategies.linear_rings)
def test_basic(linear_ring: LinearRing) -> None:
    result = linear_ring.edges

    assert isinstance(result, list)
    assert all(isinstance(element, Edge) for element in result)


@given(strategies.linear_rings)
def test_properties(linear_ring: LinearRing) -> None:
    result = linear_ring.edges

    assert len(result) == len(linear_ring) - 1
    assert all(edge.bottom in linear_ring and edge.top in linear_ring
               for edge in result)
