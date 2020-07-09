from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats)
from tests.utils import to_bound_with_ported_points_pair

coordinates = coordinates
points_pairs = strategies.builds(to_bound_with_ported_points_pair,
                                 coordinates, coordinates)
float_points_pairs = strategies.builds(to_bound_with_ported_points_pair,
                                       floats, floats)
