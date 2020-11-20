from _wagyu import Polygon
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.binding_tests.utils import to_bound_polygon_linear_rings
from tests.strategies import coordinates

linear_rings_lists = (planar.polygons(coordinates)
                      .map(to_bound_polygon_linear_rings))
polygons = strategies.builds(Polygon, linear_rings_lists)
