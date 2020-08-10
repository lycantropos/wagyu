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
                         BoundPortedMaybeRingsPair,
                         BoundPortedPointsListsPair,
                         BoundPortedPolygonKindsPair,
                         BoundPortedRingManagersPair,
                         BoundPortedRingsPair,
                         PortedLinearRingWithPolygonKind,
                         Strategy,
                         bound_edges_sides,
                         bound_fill_kinds,
                         bound_operation_kinds,
                         bound_polygon_kinds,
                         initialize_bounds,
                         ported_edges_sides,
                         ported_fill_kinds,
                         ported_operation_kinds,
                         ported_polygon_kinds,
                         sort_pair,
                         subsequences,
                         to_bound_with_ported_bounds_pair,
                         to_bound_with_ported_edges_pair,
                         to_bound_with_ported_linear_rings_pair,
                         to_bound_with_ported_local_minimum_lists,
                         to_bound_with_ported_points_lists_pair,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_ring_managers_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         to_pairs,
                         transpose_pairs)
from wagyu.hints import Coordinate

coordinates = coordinates
coordinates_lists = strategies.lists(coordinates)
sorted_coordinates_pairs = to_pairs(coordinates).map(sort_pair)
fill_kinds_pairs = strategies.sampled_from(list(zip(bound_fill_kinds,
                                                    ported_fill_kinds)))
polygon_kinds_pairs = strategies.sampled_from(list(zip(bound_polygon_kinds,
                                                       ported_polygon_kinds)))
operation_kinds_pairs = strategies.sampled_from(
        list(zip(bound_operation_kinds, ported_operation_kinds)))


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
local_minimum_lists_pairs = (strategies.lists(linear_rings_pairs)
                             .flatmap(to_linear_rings_with_polygon_kinds)
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
non_empty_points_lists_pairs = (strategies.lists(points_pairs,
                                                 min_size=1)
                                .map(transpose_pairs))


def to_rings(pairs: Strategy[BoundPortedMaybeRingsPair],
             hot_pixels_pairs: Strategy[BoundPortedPointsListsPair]
             = points_lists_pairs) -> Strategy[BoundPortedRingsPair]:
    return strategies.builds(to_bound_with_ported_rings_pair, sizes,
                             strategies.lists(pairs).map(transpose_pairs),
                             hot_pixels_pairs, booleans)


nones_pairs = to_pairs(strategies.none())
maybe_rings_pairs = strategies.recursive(nones_pairs, to_rings)
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = to_rings(maybe_rings_pairs)
non_empty_rings_pairs = to_rings(maybe_rings_pairs,
                                 non_empty_points_lists_pairs)
edges_pairs = strategies.builds(to_bound_with_ported_edges_pair, points_pairs,
                                points_pairs)
non_empty_edges_lists_pairs = strategies.lists(edges_pairs,
                                               min_size=1).map(transpose_pairs)
edges_sides_pairs = strategies.sampled_from(list(zip(bound_edges_sides,
                                                     ported_edges_sides)))
bounds_pairs = strategies.builds(to_bound_with_ported_bounds_pair,
                                 non_empty_edges_lists_pairs, sizes, sizes,
                                 points_pairs, maybe_rings_pairs, floats,
                                 sizes, integers_32, integers_32, trits,
                                 polygon_kinds_pairs, edges_sides_pairs)
non_empty_bounds_pairs = strategies.builds(
        to_bound_with_ported_bounds_pair, non_empty_edges_lists_pairs, sizes,
        sizes, points_pairs, non_empty_rings_pairs, floats, sizes, integers_32,
        integers_32, trits, polygon_kinds_pairs, edges_sides_pairs)
non_empty_bounds_lists_pairs = (strategies.lists(non_empty_bounds_pairs,
                                                 min_size=1)
                                .map(transpose_pairs))


def to_bounds_lists_pairs_indices(
        lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, int]]:
    bound_list, _ = lists_pair
    return strategies.tuples(strategies.just(lists_pair),
                             strategies.integers(0, len(bound_list) - 1))


non_empty_bounds_lists_pairs_indices = (
    non_empty_bounds_lists_pairs.flatmap(to_bounds_lists_pairs_indices))


def to_bounds_lists_pairs_with_indices_pairs(
        lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, Tuple[int]]]:
    bound_list, _ = lists_pair
    indices = strategies.integers(0, len(bound_list) - 1)
    return strategies.tuples(strategies.just(lists_pair),
                             strategies.lists(indices,
                                              min_size=2,
                                              max_size=2,
                                              unique=True)
                             .map(sort_pair))


two_or_more_non_empty_bounds_lists_pairs = (
    strategies.lists(non_empty_bounds_pairs,
                     min_size=2).map(transpose_pairs))
two_or_more_non_empty_bounds_lists_pairs_with_indices_pairs = (
    two_or_more_non_empty_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_with_indices_pairs))


def to_initialized_bounds_pairs(bounds_pair: BoundPortedBoundsPair
                                ) -> Strategy[BoundPortedBoundsPair]:
    bound, ported = bounds_pair
    indices = strategies.integers(0, len(ported.edges))
    return strategies.builds(initialize_bounds,
                             strategies.just(bounds_pair),
                             strategies.lists(indices,
                                              min_size=2,
                                              max_size=2,
                                              unique=True)
                             .map(sort_pair))


initialized_bounds_pairs = bounds_pairs.flatmap(to_initialized_bounds_pairs)
initialized_non_empty_bounds_pairs = (non_empty_bounds_pairs
                                      .flatmap(to_initialized_bounds_pairs))
initialized_bounds_lists_pairs = (strategies.lists(initialized_bounds_pairs)
                                  .map(transpose_pairs))
non_empty_initialized_bounds_lists_pairs = (
    strategies.lists(initialized_bounds_pairs,
                     min_size=1).map(transpose_pairs))
non_empty_initialized_non_empty_bounds_lists_pairs = (
    strategies.lists(initialized_non_empty_bounds_pairs,
                     min_size=1).map(transpose_pairs))
non_empty_initialized_non_empty_bounds_lists_pairs_with_indices = (
    non_empty_initialized_non_empty_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_indices))
two_or_more_initialized_non_empty_bounds_lists_pairs = (
    strategies.lists(initialized_non_empty_bounds_pairs,
                     min_size=2).map(transpose_pairs))
two_or_more_initialized_non_empty_bounds_lists_pairs_indices_pairs = (
    two_or_more_initialized_non_empty_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_with_indices_pairs))


def to_lists_pairs_scanbeams_ys(
        bounds_lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, List[Coordinate], Coordinate]]:
    bound_list, _ = bounds_lists_pair
    top_ys = [edge.top.y for bound in bound_list for edge in bound.edges]
    return strategies.tuples(strategies.just(bounds_lists_pair),
                             subsequences(top_ys),
                             strategies.sampled_from(top_ys))


non_empty_initialized_bounds_lists_pairs_scanbeams_ys = (
    non_empty_initialized_bounds_lists_pairs.flatmap(
            to_lists_pairs_scanbeams_ys))
non_empty_initialized_non_empty_bounds_lists_pairs_scanbeams_ys = (
    non_empty_initialized_non_empty_bounds_lists_pairs.flatmap(
            to_lists_pairs_scanbeams_ys))


def to_lists_pairs_scanbeams_ys_indices(
        bounds_lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsListsPair, List[Coordinate], Coordinate,
                    int]]:
    bound_list, _ = bounds_lists_pair
    top_ys = [edge.top.y for bound in bound_list for edge in bound.edges]
    return strategies.tuples(strategies.just(bounds_lists_pair),
                             subsequences(top_ys),
                             strategies.sampled_from(top_ys),
                             strategies.integers(0, len(bound_list) - 1))


non_empty_initialized_non_empty_bounds_lists_pairs_scanbeams_ys_indices = (
    non_empty_initialized_non_empty_bounds_lists_pairs.flatmap(
            to_lists_pairs_scanbeams_ys_indices))
non_empty_initialized_bounds_lists_pairs_indices = (
    non_empty_initialized_bounds_lists_pairs.flatmap(
            to_bounds_lists_pairs_indices))
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
rings_lists_pairs = strategies.lists(rings_pairs).map(transpose_pairs)
ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair, maybe_rings_lists_pairs,
        points_lists_pairs, sizes, rings_lists_pairs, sizes)
maybe_non_empty_rings_pairs = to_maybe_pairs(non_empty_rings_pairs)
maybe_non_empty_rings_lists_pairs = (
    strategies.lists(maybe_non_empty_rings_pairs).map(transpose_pairs))
non_empty_ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair,
        maybe_non_empty_rings_lists_pairs, non_empty_points_lists_pairs,
        sizes, rings_lists_pairs, sizes)


def to_initialized_ring_managers_pairs(
        pair: BoundPortedRingManagersPair
) -> Strategy[BoundPortedRingManagersPair]:
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
    non_empty_ring_managers_pairs.flatmap(to_initialized_ring_managers_pairs))


def to_ring_managers_pairs_indices_pair(
        pair: BoundPortedRingManagersPair
) -> Strategy[Tuple[BoundPortedRingManagersPair, Tuple[int, int]]]:
    bound, _ = pair
    indices = strategies.integers(0, len(bound.hot_pixels))
    return (strategies.tuples(strategies.just(pair),
                              to_pairs(indices).map(sort_pair)))


initialized_non_empty_hot_pixels_ring_managers_pairs_indices_pair = (
    initialized_non_empty_hot_pixels_ring_managers_pairs.flatmap(
            to_ring_managers_pairs_indices_pair))
