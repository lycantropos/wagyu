from typing import (List,
                    Tuple)

from _wagyu import (LinearRing,
                    LocalMinimumList,
                    PolygonKind)
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (Strategy,
                         bound_polygon_kinds,
                         to_bound_linear_rings_points,
                         to_bound_polygon_linear_rings)

linear_rings_points = (planar.contours(coordinates)
                       .map(to_bound_linear_rings_points))
linear_rings = strategies.builds(LinearRing, linear_rings_points)
polygon_kinds = strategies.sampled_from(bound_polygon_kinds)
linear_rings_lists = (planar.polygons(coordinates)
                      .map(to_bound_polygon_linear_rings))
empty_local_minimum_lists = strategies.builds(LocalMinimumList)


def to_local_minimum_list(linear_rings_with_polygon_kinds
                          : List[Tuple[LinearRing, PolygonKind]]
                          ) -> LocalMinimumList:
    result = LocalMinimumList()
    for linear_ring, polygon_kind in linear_rings_with_polygon_kinds:
        result.add_linear_ring(linear_ring, polygon_kind)
    return result


def to_linear_rings_with_polygon_kinds(
        linear_rings: List[LinearRing]) -> Strategy[List[Tuple[LinearRing,
                                                               PolygonKind]]]:
    return (strategies.builds(zip,
                              strategies.just(linear_rings),
                              strategies.lists(polygon_kinds,
                                               min_size=len(linear_rings),
                                               max_size=len(linear_rings)))
            .map(list))


non_empty_local_minimum_lists = (linear_rings_lists
                                 .flatmap(to_linear_rings_with_polygon_kinds)
                                 .map(to_local_minimum_list))
local_minimum_lists = empty_local_minimum_lists | non_empty_local_minimum_lists
