from hypothesis import given

from tests.utils import (BoundPortedBoundsPair,
                         BoundPortedFillKindsPair,
                         equivalence)
from . import strategies


@given(strategies.bounds_pairs, strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs)
def test_basic(pair: BoundPortedBoundsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair) -> None:
    bound, ported = pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair

    assert equivalence(bound.is_even_odd_alt_fill_kind(bound_subject_fill_kind,
                                                       bound_clip_fill_kind),
                       ported.is_even_odd_alt_fill_kind(
                               ported_subject_fill_kind,
                               ported_clip_fill_kind))
