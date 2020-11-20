from typing import Tuple

from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedBoundsListsPair,
    BoundPortedPointsPair,
    BoundPortedRingManagersPair,
    are_bound_ported_bounds_equal,
    are_bound_ported_ring_managers_equal,
    are_bound_ported_bounds_lists_equal)
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies
       .non_empty_initialized_non_empty_bounds_lists_pairs_with_indices,
       strategies.points_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               active_bounds_pair_index: Tuple[BoundPortedBoundsListsPair,
                                               int],
               points_pair: BoundPortedPointsPair) -> None:
    bound, ported = pair
    ((bound_active_bounds, ported_active_bounds),
     index) = active_bounds_pair_index
    bound_point, ported_point = points_pair
    ported_bound = ported_active_bounds[index]

    bound_active_bounds = bound.add_point(index, bound_active_bounds,
                                          bound_point)
    ported.add_point(ported_bound, ported_active_bounds, ported_point)

    assert are_bound_ported_bounds_equal(bound_active_bounds[index],
                                         ported_bound)
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
