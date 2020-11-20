from _wagyu import LinearRing
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.binding_tests.utils import to_bound_points_list
from tests.strategies import coordinates

linear_rings_points = planar.contours(coordinates).map(to_bound_points_list)
linear_rings = strategies.builds(LinearRing, linear_rings_points)
