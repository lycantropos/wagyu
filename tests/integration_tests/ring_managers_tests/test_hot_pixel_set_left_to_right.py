from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies
       .initialized_non_empty_hot_pixels_ring_managers_pairs_indices_pair,
       strategies.coordinates,
       strategies.sorted_coordinates_pairs,
       strategies.initialized_non_empty_bounds_pairs,
       strategies.booleans)
def test_basic(pair_start_stop: Tuple[BoundPortedRingManagersPair,
                                      Tuple[int, int]],
               y: Coordinate,
               start_x_end_x: Tuple[Coordinate, Coordinate],
               bounds_pair: BoundPortedBoundsPair,
               add_end_point: bool) -> None:
    (bound, ported), (start, stop) = pair_start_stop
    start_x, end_x = start_x_end_x
    bound_bound, ported_bound = bounds_pair

    ported_result = ported.hot_pixel_set_left_to_right(
            y, start_x, end_x, ported_bound, start, stop, add_end_point)
    bound_result = bound.hot_pixel_set_left_to_right(
            y, start_x, end_x, bound_bound, start, stop, add_end_point)

    assert bound_result == ported_result
    assert are_bound_ported_bounds_equal(bound_bound, ported_bound)
    assert are_bound_ported_ring_managers_equal(bound, ported)
