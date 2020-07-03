from _wagyu import Multipolygon
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import to_bound_multipolygon_polygons

polygons_lists = (planar.multipolygons(coordinates)
                  .map(to_bound_multipolygon_polygons))
multipolygons = strategies.builds(Multipolygon, polygons_lists)
