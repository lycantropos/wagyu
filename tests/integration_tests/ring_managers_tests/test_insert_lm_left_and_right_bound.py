from typing import (List,
                    Tuple)

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
       strategies.operation_kinds_pairs, strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs, strategies.coordinates_lists,
       strategies
       .two_or_more_initialized_non_empty_bounds_lists_pairs_indices_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               scanbeams: List[Coordinate],
               active_bounds_pair_indices_pair
               : Tuple[BoundPortedBoundsListsPair, Tuple[int, int]]) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    bound_scanbeams, ported_scanbeams = scanbeams, scanbeams[:]
    ((bound_active_bounds, ported_active_bounds),
     (first_index, second_index)) = active_bounds_pair_indices_pair
    ported_first_bound = ported_active_bounds[first_index]
    ported_second_bound = ported_active_bounds[second_index]

    bound_scanbeams, bound_active_bounds = (
        bound.insert_lm_left_and_right_bound(
                bound_operation_kind, bound_subject_fill_kind,
                bound_clip_fill_kind, bound_scanbeams, first_index,
                second_index, bound_active_bounds))
    ported.insert_lm_left_and_right_bound(
            ported_operation_kind, ported_subject_fill_kind,
            ported_clip_fill_kind, ported_scanbeams, ported_first_bound,
            ported_second_bound, ported_active_bounds)

    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
