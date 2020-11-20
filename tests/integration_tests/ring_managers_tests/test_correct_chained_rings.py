from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedRingManagersPair,
    are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs)
def test_basic(pair: BoundPortedRingManagersPair) -> None:
    bound, ported = pair

    bound.correct_chained_rings()
    ported.correct_chained_rings()

    assert are_bound_ported_ring_managers_equal(bound, ported)
