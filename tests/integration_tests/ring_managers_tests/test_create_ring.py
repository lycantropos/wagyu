from hypothesis import given

from tests.utils import (BoundPortedRingManagersPair,
                         are_bound_ported_ring_managers_equal,
                         are_bound_ported_rings_equal)
from . import strategies


@given(strategies.ring_managers_pairs)
def test_basic(pair: BoundPortedRingManagersPair) -> None:
    bound, ported = pair

    bound_result = bound.create_ring()
    ported_result = ported.create_ring()

    assert are_bound_ported_rings_equal(bound_result, ported_result)
    assert are_bound_ported_ring_managers_equal(bound, ported)
