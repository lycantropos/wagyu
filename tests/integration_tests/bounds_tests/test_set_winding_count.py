from typing import Tuple

from _wagyu import set_winding_count as bound
from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedFillKindsPair,
                         are_bound_ported_bounds_lists_equal)
from wagyu.bound import set_winding_count as ported
from . import strategies


@given(strategies.non_empty_bounds_lists_pairs_indices,
       strategies.fill_kinds_pairs, strategies.fill_kinds_pairs)
def test_basic(lists_pair_index: Tuple[BoundPortedBoundsListsPair, int],
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair) -> None:
    (bound_list, ported_list), index = lists_pair_index
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair

    bound_list = bound(index, bound_list, bound_subject_fill_kind,
                       bound_clip_fill_kind)
    ported(index, ported_list, ported_subject_fill_kind, ported_clip_fill_kind)

    assert are_bound_ported_bounds_lists_equal(bound_list, ported_list)
