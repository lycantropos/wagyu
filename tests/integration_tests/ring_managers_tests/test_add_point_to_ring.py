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
       strategies.points_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               bounds_pair: BoundPortedBoundsPair,
               points_pair: BoundPortedPointsPair) -> None:
    bound, ported = pair
    bound_bound, ported_bound = bounds_pair
    bound_point, ported_point = points_pair

    ported.add_point_to_ring(ported_bound, ported_point)
    bound.add_point_to_ring(bound_bound, bound_point)

    assert are_bound_ported_bounds_equal(bound_bound, ported_bound)
    assert are_bound_ported_ring_managers_equal(bound, ported)
