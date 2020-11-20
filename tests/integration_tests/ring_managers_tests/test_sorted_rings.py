from hypothesis import given

from tests.integration_tests.utils import (BoundPortedRingManagersPair,
                                           are_bound_ported_rings_lists_equal)
from . import strategies


@given(strategies.ring_managers_pairs)
def test_basic(pair: BoundPortedRingManagersPair) -> None:
    bound, ported = pair

    assert are_bound_ported_rings_lists_equal(bound.sorted_rings,
                                              ported.sorted_rings)
