import pytest
from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedOperationKindsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies.coordinates, strategies.operation_kinds_pairs,
       strategies.fill_kinds_pairs, strategies.fill_kinds_pairs,
       strategies.two_or_more_initialized_non_empty_bounds_lists_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               top_y: Coordinate,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               active_bounds_pair: BoundPortedBoundsListsPair) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    bound_active_bounds, ported_active_bounds = active_bounds_pair

    try:
        bound_active_bounds = bound.process_intersections(
                top_y, bound_operation_kind, bound_subject_fill_kind,
                bound_clip_fill_kind, bound_active_bounds)
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported.process_intersections(top_y, ported_operation_kind,
                                         ported_subject_fill_kind,
                                         ported_clip_fill_kind,
                                         ported_active_bounds)
    else:
        ported.process_intersections(top_y, ported_operation_kind,
                                     ported_subject_fill_kind,
                                     ported_clip_fill_kind,
                                     ported_active_bounds)

        assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                                   ported_active_bounds)
        assert are_bound_ported_ring_managers_equal(bound, ported)
