from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.local_minimum_lists_pairs_indices_coordinates,
       strategies.initialized_bounds_lists_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               local_minimum_lists_pair_index_top_y
               : Tuple[BoundPortedLocalMinimumListsPair, int, Coordinate],
               active_bounds_pair: BoundPortedBoundsListsPair
               ) -> None:
    bound, ported = pair
    ((bound_local_minimum_list, ported_local_minimum_list), index,
     top_y) = local_minimum_lists_pair_index_top_y
    bound_active_bounds, ported_active_bounds = active_bounds_pair
    bound_scanbeams = bound_local_minimum_list.scanbeams
    ported_scanbeams = ported_local_minimum_list.scanbeams

    (bound_active_bounds, bound_scanbeams,
     bound_result) = bound.insert_local_minima_into_abl_hot_pixel(
            top_y, bound_local_minimum_list, index, bound_active_bounds,
            bound_scanbeams)
    ported_result = ported.insert_local_minima_into_abl_hot_pixel(
            top_y, ported_local_minimum_list, index, ported_active_bounds,
            ported_scanbeams)

    assert bound_result == ported_result
    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
