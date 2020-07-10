from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import (coordinates,
                              sizes)
from tests.utils import (BoundLinearRingWithPolygonKind,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedPolygonKindsPair,
                         PortedLinearRingWithPolygonKind,
                         Strategy,
                         bound_polygons_kinds,
                         ported_polygons_kinds,
                         to_bound_with_ported_linear_rings,
                         to_bound_with_ported_linear_rings_points,
                         to_bound_with_ported_local_minimum_lists,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_ring_managers_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)

polygons_kinds_pairs = strategies.sampled_from(
        list(zip(bound_polygons_kinds, ported_polygons_kinds)))


def to_linear_rings_with_polygons_kinds(
        linear_rings_pairs: List[BoundPortedLocalMinimumListsPair]
) -> Strategy[Tuple[List[BoundLinearRingWithPolygonKind],
                    List[PortedLinearRingWithPolygonKind]]]:
    bound_linear_rings, ported_linear_rings = transpose_pairs(
            linear_rings_pairs)

    def merge_with_linear_rings(
            polygons_kinds: List[BoundPortedPolygonKindsPair]
    ) -> Tuple[List[BoundLinearRingWithPolygonKind],
               List[PortedLinearRingWithPolygonKind]]:
        bound_kinds, ported_kinds = transpose_pairs(polygons_kinds)
        return (list(zip(bound_linear_rings, bound_kinds)),
                list(zip(ported_linear_rings, ported_kinds)))

    return (strategies.lists(polygons_kinds_pairs,
                             min_size=len(bound_linear_rings),
                             max_size=len(bound_linear_rings))
            .map(merge_with_linear_rings))


linear_rings_points_pairs = planar.contours(coordinates).map(
        to_bound_with_ported_linear_rings_points)
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings))
local_minimum_lists_pairs = (strategies.lists(linear_rings_pairs)
                             .flatmap(to_linear_rings_with_polygons_kinds)
                             .map(to_bound_with_ported_local_minimum_lists))
booleans = strategies.booleans()
sizes = sizes
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs, booleans)
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
rings_lists_pairs = strategies.lists(rings_pairs).map(transpose_pairs)
ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair, maybe_rings_lists_pairs,
        points_lists_pairs, rings_lists_pairs, sizes)
