from typing import (List,
                    Tuple)

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.non_empty_initialized_bounds_lists_pairs_scanbeams_top_y)
def test_basic(pair: BoundPortedRingManagersPair,
               active_bounds_pair_scanbeams_top_y
               : Tuple[BoundPortedBoundsListsPair, List[Coordinate],
                       Coordinate]) -> None:
    bound, ported = pair
    ((bound_active_bounds, ported_active_bounds), scanbeams,
     top_y) = active_bounds_pair_scanbeams_top_y
    bound_scanbeams, ported_scanbeams = scanbeams, scanbeams[:]

    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)

    bound_result, bound_scanbeams = (
        bound.process_hot_pixel_edges_at_top_of_scanbeam(top_y,
                                                         bound_scanbeams,
                                                         bound_active_bounds))
    ported_result = ported.process_hot_pixel_edges_at_top_of_scanbeam(
            top_y, ported_scanbeams, ported_active_bounds)

    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_bounds_lists_equal(bound_result, ported_result)
    assert are_bound_ported_ring_managers_equal(bound, ported)
