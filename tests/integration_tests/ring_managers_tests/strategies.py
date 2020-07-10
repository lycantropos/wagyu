from hypothesis import strategies

from tests.strategies import (coordinates,
                              sizes)
from tests.utils import (to_bound_with_ported_points_nodes_pair,
                         to_bound_with_ported_points_pair,
                         to_bound_with_ported_ring_managers_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)

booleans = strategies.booleans()
sizes = sizes
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
points_nodes_pairs = strategies.builds(to_bound_with_ported_points_nodes_pair,
                                       coordinates, coordinates)
maybe_points_nodes_pairs = to_maybe_pairs(points_nodes_pairs)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs,
                                maybe_points_nodes_pairs,
                                maybe_points_nodes_pairs, booleans)
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
points_nodes_lists_pairs = (strategies.lists(points_nodes_pairs)
                            .map(transpose_pairs))
maybe_points_nodes_lists_pairs = (strategies.lists(maybe_points_nodes_pairs)
                                  .map(transpose_pairs))
rings_lists_pairs = strategies.lists(rings_pairs).map(transpose_pairs)
ring_managers_pairs = strategies.builds(
        to_bound_with_ported_ring_managers_pair, maybe_rings_lists_pairs,
        maybe_points_nodes_lists_pairs, points_lists_pairs,
        points_nodes_lists_pairs, rings_lists_pairs, points_nodes_lists_pairs,
        sizes)
