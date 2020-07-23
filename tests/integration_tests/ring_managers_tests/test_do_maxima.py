from typing import Tuple

import pytest
from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedOperationKindsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_maybe_bounds_lists_equal,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.initialized_non_empty_hot_pixels_ring_managers_pairs,
       strategies.operation_kinds_pairs, strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs,
       strategies
       .two_or_more_initialized_non_empty_bounds_lists_pairs_indices_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair,
               active_bounds_pair_indices_pair
               : Tuple[BoundPortedBoundsListsPair, Tuple[int, int]]) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair
    ((bound_active_bounds, ported_active_bounds),
     (bound_index, bound_maximum_index)) = active_bounds_pair_indices_pair

    try:
        bound_active_bounds, bound_result = bound.do_maxima(
                bound_operation_kind, bound_subject_fill_kind,
                bound_clip_fill_kind, bound_index, bound_maximum_index,
                bound_active_bounds)
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported.do_maxima(ported_operation_kind, ported_subject_fill_kind,
                             ported_clip_fill_kind, bound_index,
                             bound_maximum_index, ported_active_bounds)
    else:
        ported_result = ported.do_maxima(ported_operation_kind,
                                         ported_subject_fill_kind,
                                         ported_clip_fill_kind, bound_index,
                                         bound_maximum_index,
                                         ported_active_bounds)

        assert bound_result == ported_result
        assert are_bound_ported_maybe_bounds_lists_equal(bound_active_bounds,
                                                         ported_active_bounds)
        assert are_bound_ported_ring_managers_equal(bound, ported)
