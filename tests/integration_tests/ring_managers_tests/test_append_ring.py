from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_equal,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.two_or_more_non_empty_bounds_lists_pairs_with_indices_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               active_bounds_pair_indices_pair
               : Tuple[BoundPortedBoundsListsPair, Tuple[int, int]]) -> None:
    bound, ported = pair
    ((bound_active_bounds, ported_active_bounds),
     (first_index, second_index)) = active_bounds_pair_indices_pair
    ported_first_bound = ported_active_bounds[first_index]
    ported_second_bound = ported_active_bounds[second_index]

    bound_active_bounds = bound.append_ring(first_index, second_index,
                                            bound_active_bounds)
    ported.append_ring(ported_first_bound, ported_second_bound,
                       ported_active_bounds)

    assert are_bound_ported_bounds_equal(bound_active_bounds[first_index],
                                         ported_first_bound)
    assert are_bound_ported_bounds_equal(bound_active_bounds[second_index],
                                         ported_second_bound)
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
