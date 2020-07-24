from typing import Tuple

from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              integers_32,
                              sizes,
                              trits)
from tests.utils import (BoundPortedBoundsListsPair,
                         BoundPortedBoundsPair,
                         Strategy,
                         bound_edges_sides,
                         bound_fill_kinds,
                         bound_polygon_kinds,
                         initialize_bounds,
                         ported_edges_sides,
                         ported_fill_kinds,
                         ported_polygon_kinds,
                         sort_pair,
                         to_bound_with_ported_bounds_pair,
                         to_bound_with_ported_edges_pair,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)

booleans = strategies.booleans()
sizes = sizes
coordinates_lists = strategies.lists(coordinates)
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs,
                                points_lists_pairs, booleans)
fill_kinds_pairs = strategies.sampled_from(list(zip(bound_fill_kinds,
                                                    ported_fill_kinds)))
polygon_kinds_pairs = strategies.sampled_from(
        list(zip(bound_polygon_kinds, ported_polygon_kinds)))
edges_sides_pairs = strategies.sampled_from(list(zip(bound_edges_sides,
                                                     ported_edges_sides)))
edges_pairs = strategies.builds(to_bound_with_ported_edges_pair, points_pairs,
                                points_pairs)
non_empty_edges_lists_pairs = (strategies.lists(edges_pairs,
                                                min_size=1)
                               .map(transpose_pairs))
bounds_pairs = strategies.builds(to_bound_with_ported_bounds_pair,
                                 non_empty_edges_lists_pairs, sizes, sizes,
                                 points_pairs, maybe_rings_pairs, floats,
                                 sizes, integers_32, integers_32, trits,
                                 polygon_kinds_pairs,
                                 edges_sides_pairs)
non_empty_bounds_lists_pairs = (strategies.lists(bounds_pairs,
                                                 min_size=1)
                                .map(transpose_pairs))


def to_bounds_lists_pairs_indices(
        bounds_lists_pair: BoundPortedBoundsListsPair
) -> Strategy[Tuple[BoundPortedBoundsPair, int]]:
    _, ported = bounds_lists_pair
    return strategies.tuples(strategies.just(bounds_lists_pair),
                             strategies.integers(0, len(ported) - 1))


non_empty_bounds_lists_pairs_indices = (
    non_empty_bounds_lists_pairs.flatmap(to_bounds_lists_pairs_indices))


def to_initialized_bounds_pairs(bounds_pair: BoundPortedBoundsPair
                                ) -> Strategy[BoundPortedBoundsPair]:
    bound, ported = bounds_pair
    indices = strategies.integers(0, len(ported.edges))
    return strategies.builds(initialize_bounds, strategies.just(bounds_pair),
                             strategies.lists(indices,
                                              min_size=2,
                                              max_size=2,
                                              unique=True)
                             .map(sort_pair))


initialized_bounds_pairs = (bounds_pairs
                            .flatmap(to_initialized_bounds_pairs))
initialized_bounds_lists_pairs = (strategies.lists(initialized_bounds_pairs)
                                  .map(transpose_pairs))
