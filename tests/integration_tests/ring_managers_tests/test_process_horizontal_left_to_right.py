from typing import (List,
                    Tuple)

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedOperationKindsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_maybe_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies.operation_kinds_pairs, strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs,
       strategies
       .non_empty_initialized_non_empty_bounds_lists_pairs_scanbeams_ys_indices
       )
def test_basic(pair: BoundPortedRingManagersPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               active_bounds_pair_scanbeams_scanline_y_index
               : Tuple[BoundPortedBoundsListsPair, List[Coordinate],
                       Coordinate, int]) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    ((bound_active_bounds, ported_active_bounds), scanbeams, scanline_y,
     index) = active_bounds_pair_scanbeams_scanline_y_index
    bound_scanbeams, ported_scanbeams = scanbeams, scanbeams[:]

    ported_result = ported.process_horizontal_left_to_right(
            ported_operation_kind, ported_subject_fill_kind,
            ported_clip_fill_kind, scanline_y, ported_scanbeams, index,
            ported_active_bounds)
    (bound_active_bounds, bound_scanbeams,
     bound_result) = bound.process_horizontal_left_to_right(
            bound_operation_kind, bound_subject_fill_kind,
            bound_clip_fill_kind, scanline_y, bound_scanbeams, index,
            bound_active_bounds)

    assert bound_result == ported_result
    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_maybe_bounds_lists_equal(bound_active_bounds,
                                                     ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
