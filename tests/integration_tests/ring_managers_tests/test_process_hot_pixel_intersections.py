import pytest
from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.coordinates,
       strategies.initialized_bounds_lists_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               top_y: Coordinate,
               active_bounds_pair: BoundPortedBoundsListsPair) -> None:
    bound, ported = pair
    bound_active_bounds, ported_active_bounds = active_bounds_pair

    try:
        bound_result = bound.process_hot_pixel_intersections(
                top_y, bound_active_bounds)
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported.process_hot_pixel_intersections(top_y, ported_active_bounds)
    else:
        ported_result = ported.process_hot_pixel_intersections(
                top_y, ported_active_bounds)

        assert are_bound_ported_bounds_lists_equal(bound_result, ported_result)
        assert are_bound_ported_ring_managers_equal(bound, ported)
