from _wagyu import (LinearRing,
                    Wagyu)
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (bound_polygons_kinds,
                         to_bound_linear_rings_points)

polygons_kinds = strategies.sampled_from(bound_polygons_kinds)
linear_rings_points = (planar.contours(coordinates)
                       .map(to_bound_linear_rings_points))
linear_rings = strategies.builds(LinearRing, linear_rings_points)
empty_wagyus = strategies.builds(Wagyu)
