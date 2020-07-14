from typing import (List,
                    Tuple)

import _wagyu
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import (coordinates,
                              floats,
                              integers_32,
                              sizes,
                              trits)
from tests.utils import (BoundLinearRingWithPolygonKind,
                         BoundPortedBoundsPair,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedPolygonKindsPair,
                         PortedLinearRingWithPolygonKind,
                         Strategy,
                         bound_edges_sides, bound_polygons_kinds,
                         initialize_bounds, ported_edges_sides,
                         ported_polygons_kinds,
                         to_bound_with_ported_bounds_pair,
                         to_bound_with_ported_edges_lists,
                         to_bound_with_ported_linear_rings,
                         to_bound_with_ported_linear_rings_points,
                         to_bound_with_ported_local_minimum_lists,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_ring_managers_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         to_pairs,
                         transpose_pairs)
from wagyu.linear_ring import LinearRing
from wagyu.point import Point

coordinates = coordinates
polygons_kinds_pairs = strategies.sampled_from(
        list(zip(bound_polygons_kinds, ported_polygons_kinds)))


def to_linear_rings_with_polygons_kinds(
        linear_rings_pairs: List[BoundPortedLocalMinimumListsPair]
) -> Strategy[Tuple[List[BoundLinearRingWithPolygonKind],
                    List[PortedLinearRingWithPolygonKind]]]:
    bound_linear_rings, ported_linear_rings = transpose_pairs(
            linear_rings_pairs)
    bound_linear_rings = [_wagyu.LinearRing(
            [_wagyu.Point(1, 0), _wagyu.Point(0, 1), _wagyu.Point(0, 0),
             _wagyu.Point(1, 0)]), _wagyu.LinearRing(
            [_wagyu.Point(-1, 0), _wagyu.Point(1, 0), _wagyu.Point(1, 1),
             _wagyu.Point(-1, 1), _wagyu.Point(-1, 0)])]
    ported_linear_rings = [
        LinearRing([Point(1, 0), Point(0, 1), Point(0, 0), Point(1, 0)]),
        LinearRing([Point(-1, 0), Point(1, 0), Point(1, 1), Point(-1, 1),
                    Point(-1, 0)])]

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


def to_local_minimum_lists_pairs_with_indices(
        local_minimum_lists_pair: BoundPortedLocalMinimumListsPair
) -> Strategy[Tuple[BoundPortedLocalMinimumListsPair, int]]:
    bound_local_minimum_list, _ = local_minimum_lists_pair
    indices = strategies.integers(0, max(len(bound_local_minimum_list) - 1, 0))
    return strategies.tuples(strategies.just(local_minimum_lists_pair),
                             indices)


local_minimum_lists_pairs_with_indices = local_minimum_lists_pairs.flatmap(
        to_local_minimum_lists_pairs_with_indices)
booleans = strategies.booleans()
sizes = sizes
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs, booleans)
edges_lists_pairs = linear_rings_pairs.map(to_bound_with_ported_edges_lists)
edges_sides_pairs = strategies.sampled_from(list(zip(bound_edges_sides,
                                                     ported_edges_sides)))
bounds_pairs = strategies.builds(to_bound_with_ported_bounds_pair,
                                 edges_lists_pairs, points_pairs,
                                 maybe_rings_pairs, floats, sizes, integers_32,
                                 integers_32, trits, polygons_kinds_pairs,
                                 edges_sides_pairs)


def to_initialized_bounds_pairs(bounds_pair: BoundPortedBoundsPair
                                ) -> Strategy[BoundPortedBoundsPair]:
    bound, ported = bounds_pair
    return strategies.builds(initialize_bounds,
                             strategies.just(bounds_pair),
                             strategies.integers(0, len(ported.edges) - 1))


initialized_bounds_pairs = bounds_pairs.flatmap(to_initialized_bounds_pairs)
initialized_bounds_lists_pairs = (strategies.lists(initialized_bounds_pairs)
                                  .map(transpose_pairs))
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
rings_lists_pairs = strategies.lists(rings_pairs).map(transpose_pairs)
ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair,
        to_pairs(strategies.builds(list)),
        to_pairs(strategies.builds(list)), to_pairs(strategies.builds(list)),
        sizes)
