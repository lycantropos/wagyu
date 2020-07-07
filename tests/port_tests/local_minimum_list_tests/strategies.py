from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import (Strategy,
                         to_ported_linear_rings_points,
                         to_bound_polygon_linear_rings)
from wagyu.enums import PolygonKind
from wagyu.linear_ring import LinearRing
from wagyu.local_minimum import LocalMinimumList

linear_rings_points = (planar.contours(coordinates)
                       .map(to_ported_linear_rings_points))
linear_rings = strategies.builds(LinearRing, linear_rings_points)
polygons_kinds = strategies.sampled_from(list(PolygonKind.__members__
                                              .values()))
linear_rings_lists = (planar.polygons(coordinates)
                      .map(to_bound_polygon_linear_rings))
empty_local_minimum_lists = strategies.builds(LocalMinimumList)


def to_local_minimum_list(linear_rings_with_polygons_kinds
                          : List[Tuple[LinearRing, PolygonKind]]
                          ) -> LocalMinimumList:
    result = LocalMinimumList()
    for linear_ring, polygon_kind in linear_rings_with_polygons_kinds:
        result.add_linear_ring(linear_ring, polygon_kind)
    return result


def to_linear_rings_with_polygons_kinds(
        linear_rings: List[LinearRing]) -> Strategy[List[Tuple[LinearRing,
                                                               PolygonKind]]]:
    return (strategies.builds(zip,
                              strategies.just(linear_rings),
                              strategies.lists(polygons_kinds,
                                               min_size=len(linear_rings),
                                               max_size=len(linear_rings)))
            .map(list))


non_empty_local_minimum_lists = (linear_rings_lists
                                 .flatmap(to_linear_rings_with_polygons_kinds)
                                 .map(to_local_minimum_list))
local_minimum_lists = empty_local_minimum_lists | non_empty_local_minimum_lists
