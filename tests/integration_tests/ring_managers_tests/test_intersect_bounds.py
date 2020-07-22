from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedOperationKindsPair,
                         BoundPortedPointsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_equal,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies.points_pairs, strategies.operation_kinds_pairs,
       strategies.fill_kinds_pairs, strategies.fill_kinds_pairs,
       strategies
       .two_or_more_initialized_non_empty_bounds_lists_pairs_with_indices_pairs
       )
def test_basic(pair: BoundPortedRingManagersPair,
               points_pair: BoundPortedPointsPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               active_bounds_pair_indices_pair
               : Tuple[BoundPortedBoundsListsPair, Tuple[int, int]]) -> None:
    bound, ported = pair
    bound_point, ported_point = points_pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    ((bound_active_bounds, ported_active_bounds),
     (first_index, second_index)) = active_bounds_pair_indices_pair
    ported_first_bound = ported_active_bounds[first_index]
    ported_second_bound = ported_active_bounds[second_index]

    bound_active_bounds = bound.intersect_bounds(
            bound_point, bound_operation_kind, bound_subject_fill_kind,
            bound_clip_fill_kind, first_index, second_index,
            bound_active_bounds)
    ported.intersect_bounds(ported_point, ported_operation_kind,
                            ported_subject_fill_kind, ported_clip_fill_kind,
                            ported_first_bound, ported_second_bound,
                            ported_active_bounds)

    assert are_bound_ported_bounds_equal(bound_active_bounds[first_index],
                                         ported_first_bound)
    assert are_bound_ported_bounds_equal(bound_active_bounds[second_index],
                                         ported_second_bound)
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
