from hypothesis_geometry import planar

from tests.integration_tests.utils import (
    to_bound_with_ported_linear_rings_pair,
    to_bound_with_ported_points_lists_pair)
from tests.strategies import coordinates

linear_rings_points_pairs = (
    planar.contours(coordinates).map(
            to_bound_with_ported_points_lists_pair))
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings_pair))
