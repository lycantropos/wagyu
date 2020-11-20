from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedBoundsPair,
    BoundPortedPointsPair,
    BoundPortedRingManagersPair,
    are_bound_ported_bounds_equal,
    are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies.initialized_non_empty_bounds_pairs,
       strategies.points_pairs,
       strategies.booleans)
def test_basic(pair: BoundPortedRingManagersPair,
               bounds_pair: BoundPortedBoundsPair,
               end_points_pair: BoundPortedPointsPair,
               add_end_point: bool) -> None:
    bound, ported = pair
    bound_bound, ported_bound = bounds_pair
    bound_end_point, ported_end_point = end_points_pair

    bound.insert_hot_pixels_in_path(bound_bound, bound_end_point,
                                    add_end_point)
    ported.insert_hot_pixels_in_path(ported_bound, ported_end_point,
                                     add_end_point)

    assert are_bound_ported_bounds_equal(bound_bound, ported_bound)
    assert are_bound_ported_ring_managers_equal(bound, ported)
