from hypothesis import given

from tests.utils import (BoundPolygonKind,
                         BoundPortedFillKindsPair,
                         BoundPortedMultipolygonsPair,
                         BoundPortedWagyusPair,
                         PortedPolygonKind,
                         are_bound_ported_multipolygons_equal,
                         are_bound_ported_wagyus_equal)
from . import strategies


@given(strategies.wagyus_pairs, strategies.multipolygons_pairs,
       strategies.multipolygons_pairs, strategies.fill_kinds_pairs,
       strategies.fill_kinds_pairs)
def test_basic(wagyus_pair: BoundPortedWagyusPair,
               subjects_pair: BoundPortedMultipolygonsPair,
               clips_pair: BoundPortedMultipolygonsPair,
               subject_fill_kinds_pair: BoundPortedFillKindsPair,
               clip_fill_kinds_pair: BoundPortedFillKindsPair) -> None:
    bound, ported = wagyus_pair
    bound_subject, ported_subject = subjects_pair
    bound_clip, ported_clip = clips_pair
    bound_subject_fill_kind, ported_subject_fill_kind = subject_fill_kinds_pair
    bound_clip_fill_kind, ported_clip_fill_kind = clip_fill_kinds_pair

    for bound_subject_polygon in bound_subject:
        bound.add_polygon(bound_subject_polygon, BoundPolygonKind.SUBJECT)
    for bound_clip_polygon in bound_clip:
        bound.add_polygon(bound_clip_polygon, BoundPolygonKind.CLIP)
    for ported_subject_polygon in ported_subject:
        ported.add_polygon(ported_subject_polygon, PortedPolygonKind.SUBJECT)
    for ported_clip_polygon in ported_clip:
        ported.add_polygon(ported_clip_polygon, PortedPolygonKind.CLIP)

    bound_result = bound.symmetric_subtract(bound_subject_fill_kind,
                                            bound_clip_fill_kind)
    ported_result = ported.symmetric_subtract(ported_subject_fill_kind,
                                              ported_clip_fill_kind)

    assert are_bound_ported_multipolygons_equal(bound_result, ported_result)
    assert are_bound_ported_wagyus_equal(bound, ported)
