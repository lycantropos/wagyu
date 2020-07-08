from hypothesis import given

from tests.utils import (BoundPortedLinearRingsPair,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedPolygonKindsPair,
                         are_bound_ported_local_minimums_lists_equal)
from . import strategies


@given(strategies.empty_local_minimum_lists_pairs,
       strategies.linear_rings_pairs,
       strategies.polygons_kinds_pairs)
def test_basic(local_minimum_lists_pair: BoundPortedLocalMinimumListsPair,
               linear_rings_pair: BoundPortedLinearRingsPair,
               polygons_kinds_pair: BoundPortedPolygonKindsPair) -> None:
    (bound_local_minimum_list,
     ported_local_minimum_list) = local_minimum_lists_pair
    bound_linear_ring, ported_linear_ring = linear_rings_pair
    bound_polygon_kind, ported_polygon_kind = polygons_kinds_pair

    bound_local_minimum_list.add_linear_ring(bound_linear_ring,
                                             bound_polygon_kind)
    ported_local_minimum_list.add_linear_ring(ported_linear_ring,
                                              ported_polygon_kind)

    assert are_bound_ported_local_minimums_lists_equal(
            bound_local_minimum_list, ported_local_minimum_list)