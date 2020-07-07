from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (to_bound_with_ported_linear_rings,
                         to_bound_with_ported_linear_rings_points)

linear_rings_points_pairs = (planar.contours(coordinates)
                             .map(to_bound_with_ported_linear_rings_points))
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings))
