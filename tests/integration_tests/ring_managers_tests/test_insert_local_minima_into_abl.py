from typing import Tuple

from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedOperationKindsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.ring_managers_pairs,
       strategies.operation_kinds_pairs,
       strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs,
       strategies.local_minimum_lists_pairs_indices_coordinates,
       strategies.initialized_bounds_lists_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               local_minimum_lists_pair_index_top_y
               : Tuple[BoundPortedLocalMinimumListsPair, int, Coordinate],
               active_bounds_pair: BoundPortedBoundsListsPair
               ) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    ((bound_local_minimum_list, ported_local_minimum_list), index,
     bottom_y) = local_minimum_lists_pair_index_top_y
    bound_active_bounds, ported_active_bounds = active_bounds_pair
    bound_scanbeams = bound_local_minimum_list.scanbeams
    ported_scanbeams = ported_local_minimum_list.scanbeams

    (bound_active_bounds, bound_scanbeams,
     bound_result) = bound.insert_local_minima_into_abl(
            bound_operation_kind, bound_subject_fill_kind,
            bound_clip_fill_kind, bottom_y, bound_scanbeams,
            bound_local_minimum_list, index, bound_active_bounds)
    ported_result = ported.insert_local_minima_into_abl(
            ported_operation_kind, ported_subject_fill_kind,
            ported_clip_fill_kind, bottom_y, ported_scanbeams, 
            ported_local_minimum_list, index, ported_active_bounds)

    assert bound_result == ported_result
    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_bounds_lists_equal(bound_active_bounds,
                                               ported_active_bounds)
    assert are_bound_ported_ring_managers_equal(bound, ported)
