from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.binding_tests.utils import (BoundLinearRingWithPolygonKind,
                                       bound_polygon_kinds)
from tests.integration_tests.utils import (
    BoundPortedLocalMinimumListsPair,
    BoundPortedPolygonKindsPair,
    to_bound_with_ported_linear_rings_pair,
    to_bound_with_ported_local_minimum_lists,
    to_bound_with_ported_points_lists_pair)
from tests.port_tests.utils import (PortedLinearRingWithPolygonKind,
                                    ported_polygon_kinds)
from tests.strategies import coordinates
from tests.utils import (Strategy,
                         pack,
                         transpose_pairs)

polygon_kinds_pairs = strategies.sampled_from(
        list(zip(bound_polygon_kinds, ported_polygon_kinds)))


def to_linear_rings_with_polygon_kinds(
        linear_rings_pairs: List[BoundPortedLocalMinimumListsPair]
) -> Strategy[Tuple[List[BoundLinearRingWithPolygonKind],
                    List[PortedLinearRingWithPolygonKind]]]:
    bound_linear_rings, ported_linear_rings = transpose_pairs(
            linear_rings_pairs)

    def merge_with_linear_rings(
            polygon_kinds: List[BoundPortedPolygonKindsPair]
    ) -> Tuple[List[BoundLinearRingWithPolygonKind],
               List[PortedLinearRingWithPolygonKind]]:
        bound_kinds, ported_kinds = transpose_pairs(polygon_kinds)
        return (list(zip(bound_linear_rings, bound_kinds)),
                list(zip(ported_linear_rings, ported_kinds)))

    return (strategies.lists(polygon_kinds_pairs,
                             min_size=len(bound_linear_rings),
                             max_size=len(bound_linear_rings))
            .map(merge_with_linear_rings))


linear_rings_points_pairs = planar.contours(coordinates).map(
        to_bound_with_ported_points_lists_pair)
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings_pair))
local_minimums_pairs = (strategies.lists(linear_rings_pairs,
                                         min_size=1)
                        .flatmap(to_linear_rings_with_polygon_kinds)
                        .map(to_bound_with_ported_local_minimum_lists)
                        .map(pack(zip)).map(list)
                        .flatmap(strategies.sampled_from))
