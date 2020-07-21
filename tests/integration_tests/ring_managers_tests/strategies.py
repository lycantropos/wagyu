from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import (coordinates,
                              floats,
                              integers_32,
                              sizes,
                              trits)
from tests.utils import (BoundLinearRingWithPolygonKind,
                         BoundPortedBoundsListsPair,
                         BoundPortedBoundsPair,
                         BoundPortedLocalMinimumListsPair,
                         BoundPortedPolygonKindsPair,
                         BoundPortedRingManagersPair,
                         PortedLinearRingWithPolygonKind,
                         Strategy,
                         bound_edges_sides,
                         bound_polygons_kinds,
                         initialize_bounds,
                         ported_edges_sides,
                         ported_polygons_kinds,
                         subsequences,
                         to_bound_with_ported_bounds_pair,
                         to_bound_with_ported_edges_lists,
                         to_bound_with_ported_linear_rings,
                         to_bound_with_ported_linear_rings_points,
                         to_bound_with_ported_local_minimum_lists,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_ring_managers_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)
from wagyu.hints import Coordinate
from wagyu.point_node import PointNode

coordinates = coordinates
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


def to_local_minimum_lists_pairs_indices_coordinates(
        local_minimum_lists_pair: BoundPortedLocalMinimumListsPair
) -> Strategy[Tuple[BoundPortedLocalMinimumListsPair, int, Coordinate]]:
    bound_local_minimum_list, _ = local_minimum_lists_pair
    indices = strategies.integers(0, max(len(bound_local_minimum_list) - 1, 0))
    scanbeams = bound_local_minimum_list.scanbeams
    return strategies.tuples(strategies.just(local_minimum_lists_pair),
                             indices,
                             strategies.sampled_from(scanbeams)
                             if scanbeams
                             else coordinates)


booleans = strategies.booleans()
sizes = sizes
local_minimum_lists_pairs_indices_coordinates = (
    local_minimum_lists_pairs.flatmap(
            to_local_minimum_lists_pairs_indices_coordinates))
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs,
                                points_lists_pairs, booleans)
edges_lists_pairs = linear_rings_pairs.map(to_bound_with_ported_edges_lists)
edges_sides_pairs = strategies.sampled_from(list(zip(bound_edges_sides,
                                                     ported_edges_sides)))
bounds_pairs = strategies.builds(to_bound_with_ported_bounds_pair,
                                 edges_lists_pairs, sizes, sizes, points_pairs,
                                 maybe_rings_pairs, floats, sizes, integers_32,
                                 integers_32, trits, polygons_kinds_pairs,
                                 edges_sides_pairs)
ringed_bounds_pairs = strategies.builds(to_bound_with_ported_bounds_pair,
                                        edges_lists_pairs, sizes, sizes,
                                        points_pairs, rings_pairs, floats,
                                        sizes, integers_32, integers_32, trits,
                                        polygons_kinds_pairs,
                                        edges_sides_pairs)
non_empty_ringed_bounds_lists_pairs = (strategies.lists(ringed_bounds_pairs,
                                                        min_size=1)
                                       .map(transpose_pairs))


def to_bounds_lists_pairs_with_bounds_pairs(
        lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, int]]:
    bound_list, _ = lists_pair
    return strategies.tuples(strategies.just(lists_pair),
                             strategies.integers(0, len(bound_list) - 1))


non_empty_ringed_bounds_lists_pairs_with_indices = (
    non_empty_ringed_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_with_bounds_pairs))


def to_initialized_bounds_pairs(bounds_pair: BoundPortedBoundsPair
                                ) -> Strategy[BoundPortedBoundsPair]:
    bound, ported = bounds_pair
    return strategies.builds(initialize_bounds,
                             strategies.just(bounds_pair),
                             strategies.integers(0, len(ported.edges) - 1))


initialized_bounds_pairs = bounds_pairs.flatmap(to_initialized_bounds_pairs)
initialized_bounds_lists_pairs = (strategies.lists(initialized_bounds_pairs)
                                  .map(transpose_pairs))
non_empty_initialized_bounds_lists_pairs = (
    strategies.lists(initialized_bounds_pairs,
                     min_size=1).map(transpose_pairs))


def to_lists_pairs_scanbeams_top_y(
        bounds_lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, List[Coordinate], Coordinate]]:
    bound_list, _ = bounds_lists_pair
    top_ys = [edge.top.y for bound in bound_list for edge in bound.edges]
    return strategies.tuples(strategies.just(bounds_lists_pair),
                             subsequences(top_ys),
                             strategies.sampled_from(top_ys))


non_empty_initialized_bounds_lists_pairs_scanbeams_top_y = (
    non_empty_initialized_bounds_lists_pairs.flatmap(
            to_lists_pairs_scanbeams_top_y))


def to_bounds_lists_pairs_indices(
        bounds_lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, int]]:
    bound, _ = bounds_lists_pair
    return strategies.tuples(strategies.just(bounds_lists_pair),
                             strategies.integers(0, len(bound) - 1))


non_empty_initialized_bounds_lists_pairs_indices = (
    non_empty_initialized_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_indices))
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
rings_lists_pairs = strategies.lists(rings_pairs).map(transpose_pairs)
ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair, maybe_rings_lists_pairs,
        points_lists_pairs, sizes, rings_lists_pairs, sizes)


def to_initialized_ringed_bounds_pairs(bounds_pair: BoundPortedBoundsPair
                                       ) -> Strategy[BoundPortedBoundsPair]:
    bound, _ = bounds_pair
    return strategies.builds(initialize_bounds_and_ring_node,
                             strategies.just(bounds_pair),
                             strategies.integers(0, len(bound.edges) - 1),
                             coordinates, coordinates)


def initialize_bounds_and_ring_node(bounds_pair: BoundPortedBoundsPair,
                                    current_edge_index: int,
                                    node_x: Coordinate,
                                    node_y: Coordinate
                                    ) -> BoundPortedBoundsPair:
    bound, ported = initialize_bounds(bounds_pair, current_edge_index)
    bound.ring.set_node(node_x, node_y)
    ported.ring.node = PointNode(node_x, node_y)
    return bound, ported


initialized_ringed_bounds_pairs = (
    ringed_bounds_pairs.flatmap(to_initialized_ringed_bounds_pairs))
non_empty_points_lists_pairs = (strategies.lists(points_pairs,
                                                 min_size=1)
                                .map(transpose_pairs))
non_empty_hot_pixels_ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair, maybe_rings_lists_pairs,
        non_empty_points_lists_pairs, sizes, rings_lists_pairs, sizes)


def to_initialized_ring_managers_pairs(pair: BoundPortedRingManagersPair
                                       ) -> Strategy[
    BoundPortedRingManagersPair]:
    bound, _ = pair
    return strategies.builds(initialize_ring_managers,
                             strategies.just(pair),
                             strategies.integers(0, len(bound.hot_pixels) - 1))


def initialize_ring_managers(pair: BoundPortedRingManagersPair,
                             current_hot_pixel_index: int
                             ) -> BoundPortedRingManagersPair:
    bound, ported = pair
    bound.current_hot_pixel_index = current_hot_pixel_index
    ported.current_hot_pixel_index = current_hot_pixel_index
    return pair


initialized_non_empty_hot_pixels_ring_managers_pairs = (
    non_empty_hot_pixels_ring_managers_pairs.flatmap(
            to_initialized_ring_managers_pairs))
