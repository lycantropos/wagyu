from hypothesis import strategies

from tests.integration_tests.utils import (to_bound_with_ported_boxes_pair,
                                           to_bound_with_ported_points_pair)
from tests.strategies import coordinates
from tests.utils import (pack,
                         to_pairs)

points_pairs = strategies.builds(to_bound_with_ported_points_pair, coordinates,
                                 coordinates)
points_pairs_pairs = to_pairs(points_pairs)
boxes_pairs = points_pairs_pairs.map(pack(to_bound_with_ported_boxes_pair))
