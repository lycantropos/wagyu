from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (BoundLinearRingWithPolygonKind,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedPolygonKindsPair,
                         PortedLinearRingWithPolygonKind,
                         Strategy,
                         bound_polygon_kinds,
                         pack, ported_polygon_kinds,
                         to_bound_with_ported_linear_rings,
                         to_bound_with_ported_linear_rings_points,
                         to_bound_with_ported_local_minimum_lists,
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
        to_bound_with_ported_linear_rings_points)
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings))
local_minimums_pairs = (strategies.lists(linear_rings_pairs,
                                         min_size=1)
                        .flatmap(to_linear_rings_with_polygon_kinds)
                        .map(to_bound_with_ported_local_minimum_lists)
                        .map(pack(zip)).map(list)
                        .flatmap(strategies.sampled_from))
