from hypothesis import strategies

from tests.strategies import (coordinates,
                              sizes)
from tests.utils import (to_bound_with_ported_points_nodes_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)

booleans = strategies.booleans()
sizes = sizes
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
