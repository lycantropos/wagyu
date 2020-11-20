from typing import Tuple

from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedBoundsListsPair,
    BoundPortedRingManagersPair,
    are_bound_ported_bounds_lists_equal,
    are_bound_ported_ring_managers_equal)
from tests.utils import equivalence
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.coordinates,
       strategies.non_empty_initialized_bounds_lists_pairs_indices)
def test_basic(pair: BoundPortedRingManagersPair,
               top_y: Coordinate,
               active_bounds_pair_index: Tuple[BoundPortedBoundsListsPair, int]
               ) -> None:
    bound, ported = pair
    (bound_active_bounds,
     ported_active_bounds), index = active_bounds_pair_index

    (bound_active_bounds, bound_index,
     bound_result) = bound.horizontals_at_top_scanbeam(
            top_y, bound_active_bounds, index)
    ported_index, ported_result = ported.horizontals_at_top_scanbeam(
            top_y, ported_active_bounds, index)

    assert equivalence(bound_result, ported_result)
    assert bound_index == ported_index
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
