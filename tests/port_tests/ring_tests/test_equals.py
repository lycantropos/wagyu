from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.ring import Ring
from . import strategies


@given(strategies.rings)
def test_reflexivity(ring: Ring) -> None:
    assert ring == ring


@given(strategies.rings, strategies.rings)
def test_symmetry(first_ring: Ring, second_ring: Ring) -> None:
    assert equivalence(first_ring == second_ring, second_ring == first_ring)


@given(strategies.rings, strategies.rings,
       strategies.rings)
def test_transitivity(first_ring: Ring, second_ring: Ring, third_ring: Ring
                      ) -> None:
    assert implication(first_ring == second_ring and second_ring == third_ring,
                       first_ring == third_ring)


@given(strategies.rings, strategies.rings)
def test_connection_with_inequality(first_ring: Ring,
                                    second_ring: Ring) -> None:
    assert equivalence(not first_ring == second_ring,
                       first_ring != second_ring)
