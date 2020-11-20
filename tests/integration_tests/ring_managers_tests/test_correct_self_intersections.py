from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedRingManagersPair,
    are_bound_ported_ring_managers_equal)
from tests.utils import equivalence
from . import strategies


@given(strategies.ring_managers_pairs, strategies.booleans)
def test_basic(pair: BoundPortedRingManagersPair, correct_tree: bool) -> None:
    bound, ported = pair

    bound_result = bound.correct_self_intersections(correct_tree)
    ported_result = ported.correct_self_intersections(correct_tree)

    assert equivalence(bound_result, ported_result)
    assert are_bound_ported_ring_managers_equal(bound, ported)
