from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (bound_fill_kinds,
                         bound_polygon_kinds,
                         ported_fill_kinds,
                         ported_polygon_kinds,
                         to_bound_with_ported_linear_rings_pair,
                         to_bound_with_ported_multipolygons_pair,
                         to_bound_with_ported_points_lists_pair,
                         to_bound_with_ported_polygons_pair,
                         to_bound_with_wagyus_pair)

booleans = strategies.booleans()
wagyus_pairs = strategies.builds(to_bound_with_wagyus_pair, booleans)
linear_rings_points_pairs = (planar.contours(coordinates)
                             .map(to_bound_with_ported_points_lists_pair))
linear_rings_pairs = (linear_rings_points_pairs
                      .map(to_bound_with_ported_linear_rings_pair))
polygons_pairs = (planar.polygons(coordinates)
                  .map(to_bound_with_ported_polygons_pair))
polygon_kinds_pairs = strategies.sampled_from(
        list(zip(bound_polygon_kinds, ported_polygon_kinds)))
multipolygons_pairs = (planar.multipolygons(coordinates)
                       .map(to_bound_with_ported_multipolygons_pair))
fill_kinds_pairs = strategies.sampled_from(list(zip(bound_fill_kinds,
                                                    ported_fill_kinds)))
