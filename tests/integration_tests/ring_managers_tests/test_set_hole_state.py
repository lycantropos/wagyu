from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_equal,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.non_empty_ringed_bounds_lists_pairs_with_indices)
def test_basic(pair: BoundPortedRingManagersPair,
               active_bounds_pair_index: Tuple[BoundPortedBoundsListsPair, int]
               ) -> None:
    bound, ported = pair
    ((bound_active_bounds, ported_active_bounds),
     index) = active_bounds_pair_index
    ported_bound = ported_active_bounds[index]

    bound_active_bounds = bound.set_hole_state(index, bound_active_bounds)
    ported.set_hole_state(ported_bound, ported_active_bounds)

    assert are_bound_ported_bounds_equal(bound_active_bounds[index],
                                         ported_bound)
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
