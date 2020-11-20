from hypothesis import strategies
from hypothesis_geometry import planar

from tests.port_tests.utils import to_ported_linear_rings_points
from tests.strategies import coordinates
from wagyu.linear_ring import LinearRing

linear_rings_points = (planar.contours(coordinates)
                       .map(to_ported_linear_rings_points))
linear_rings = strategies.builds(LinearRing, linear_rings_points)
