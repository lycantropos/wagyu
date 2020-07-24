from hypothesis import given

from tests.utils import (BoundPortedBoundsPair,
                         BoundPortedFillKindsPair,
                         BoundPortedOperationKindsPair,
                         equivalence)
from . import strategies


@given(strategies.bounds_pairs, strategies.operation_kinds_pairs,
       strategies.fill_kinds_pairs, strategies.fill_kinds_pairs)
def test_basic(pair: BoundPortedBoundsPair,
               operation_kinds_pair: BoundPortedOperationKindsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair) -> None:
    bound, ported = pair
    bound_operation_kind, ported_operation_kind = operation_kinds_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair

    assert equivalence(bound.is_contributing(bound_operation_kind,
                                             bound_subject_fill_kind,
                                             bound_clip_fill_kind),
                       ported.is_contributing(ported_operation_kind,
                                              ported_subject_fill_kind,
                                              ported_clip_fill_kind))
