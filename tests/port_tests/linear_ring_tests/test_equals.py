from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.linear_ring import LinearRing
from . import strategies


@given(strategies.linear_rings)
def test_reflexivity(linear_ring: LinearRing) -> None:
    assert linear_ring == linear_ring


@given(strategies.linear_rings, strategies.linear_rings)
def test_symmetry(first_linear_ring: LinearRing,
                  second_linear_ring: LinearRing) -> None:
    assert equivalence(first_linear_ring == second_linear_ring,
                       second_linear_ring == first_linear_ring)


@given(strategies.linear_rings, strategies.linear_rings,
       strategies.linear_rings)
def test_transitivity(first_linear_ring: LinearRing,
                      second_linear_ring: LinearRing,
                      third_linear_ring: LinearRing) -> None:
    assert implication(first_linear_ring == second_linear_ring
                       and second_linear_ring == third_linear_ring,
                       first_linear_ring == third_linear_ring)


@given(strategies.linear_rings, strategies.linear_rings)
def test_connection_with_inequality(first_linear_ring: LinearRing,
                                    second_linear_ring: LinearRing) -> None:
    assert equivalence(not first_linear_ring == second_linear_ring,
                       first_linear_ring != second_linear_ring)
