from hypothesis import strategies

from tests.strategies import (coordinates,
                              sizes)
from tests.utils import (to_bound_with_ported_points_pair,
                         to_bound_with_ported_rings_pair,
                         to_maybe_pairs,
                         transpose_pairs)

booleans = strategies.booleans()
sizes = sizes
points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
points_lists_pairs = strategies.lists(points_pairs).map(transpose_pairs)
maybe_rings_pairs = to_maybe_pairs(strategies.deferred(lambda: rings_pairs))
maybe_rings_lists_pairs = (strategies.lists(maybe_rings_pairs)
                           .map(transpose_pairs))
rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                sizes, maybe_rings_lists_pairs,
                                points_lists_pairs, booleans)
non_empty_points_lists_pairs = (strategies.lists(points_pairs,
                                                 min_size=1)
                                .map(transpose_pairs))
non_empty_rings_pairs = strategies.builds(to_bound_with_ported_rings_pair,
                                          sizes, maybe_rings_lists_pairs,
                                          non_empty_points_lists_pairs,
                                          booleans)
