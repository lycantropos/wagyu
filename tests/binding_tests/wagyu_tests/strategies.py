from _wagyu import (LinearRing,
                    Polygon,
                    Wagyu)
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.binding_tests.utils import (bound_polygon_kinds,
                                       to_bound_points_list,
                                       to_bound_polygon_linear_rings)
from tests.strategies import coordinates

polygon_kinds = strategies.sampled_from(bound_polygon_kinds)
linear_rings_points = planar.contours(coordinates).map(to_bound_points_list)
linear_rings = strategies.builds(LinearRing, linear_rings_points)
linear_rings_lists = (planar.polygons(coordinates)
                      .map(to_bound_polygon_linear_rings))
polygons = strategies.builds(Polygon, linear_rings_lists)
empty_wagyus = strategies.builds(Wagyu)
