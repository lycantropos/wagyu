from hypothesis import given

from tests.utils import (BoundPortedPolygonKindsPair,
                         BoundPortedPolygonsPair,
                         BoundPortedWagyusPair,
                         are_bound_ported_wagyus_equal)
from . import strategies


@given(strategies.wagyus_pairs, strategies.polygons_pairs,
       strategies.polygon_kinds_pairs)
def test_basic(wagyus_pair: BoundPortedWagyusPair,
               polygons_pair: BoundPortedPolygonsPair,
               polygon_kinds_pair: BoundPortedPolygonKindsPair) -> None:
    bound, ported = wagyus_pair
    bound_polygon, ported_polygon = polygons_pair
    bound_polygon_kind, ported_polygon_kind = polygon_kinds_pair

    bound_result = bound.add_polygon(bound_polygon, bound_polygon_kind)
    ported_result = ported.add_polygon(ported_polygon, ported_polygon_kind)

    assert bound_result is ported_result
    assert are_bound_ported_wagyus_equal(bound, ported)
