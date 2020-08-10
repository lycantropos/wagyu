from hypothesis import given

from tests.utils import (BoundPortedLinearRingsPair,
                         BoundPortedPolygonKindsPair,
                         BoundPortedWagyusPair,
                         are_bound_ported_wagyus_equal)
from . import strategies


@given(strategies.wagyus_pairs, strategies.linear_rings_pairs,
       strategies.polygon_kinds_pairs)
def test_basic(wagyus_pair: BoundPortedWagyusPair,
               linear_rings_pair: BoundPortedLinearRingsPair,
               polygon_kinds_pair: BoundPortedPolygonKindsPair) -> None:
    bound, ported = wagyus_pair
    bound_linear_ring, ported_linear_ring = linear_rings_pair
    bound_polygon_kind, ported_polygon_kind = polygon_kinds_pair

    bound_result = bound.add_linear_ring(bound_linear_ring, bound_polygon_kind)
    ported_result = ported.add_linear_ring(ported_linear_ring,
                                           ported_polygon_kind)

    assert bound_result is ported_result
    assert are_bound_ported_wagyus_equal(bound, ported)
