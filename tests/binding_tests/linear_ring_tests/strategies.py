from _wagyu import LinearRing
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import to_bound_points_list

linear_rings_points = planar.contours(coordinates).map(to_bound_points_list)
linear_rings = strategies.builds(LinearRing, linear_rings_points)
