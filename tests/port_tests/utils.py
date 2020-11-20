from typing import (List,
                    Tuple)

from tests.utils import (RawPointsList,
                         RawPolygon,
                         enum_to_values)
from wagyu.bound import Bound as PortedBound
from wagyu.box import Box as PortedBox
from wagyu.edge import Edge as PortedEdge
from wagyu.enums import (EdgeSide as PortedEdgeSide,
                         FillKind as PortedFillKind,
                         OperationKind as PortedOperationKind,
                         PolygonKind as PortedPolygonKind)
from wagyu.intersect_node import IntersectNode as PortedIntersectNode
from wagyu.linear_ring import LinearRing as PortedLinearRing
from wagyu.local_minimum import (LocalMinimum as PortedLocalMinimum,
                                 LocalMinimumList as PortedLocalMinimumList)
from wagyu.point import Point as PortedPoint
from wagyu.polygon import (Multipolygon as PortedMultipolygon,
                           Polygon as PortedPolygon)
from wagyu.ring import Ring as PortedRing
from wagyu.ring_manager import RingManager as PortedRingManager
from wagyu.wagyu import Wagyu as PortedWagyu

PortedBound = PortedBound
PortedBox = PortedBox
PortedEdge = PortedEdge
PortedEdgeSide = PortedEdgeSide
PortedFillKind = PortedFillKind
PortedIntersectNode = PortedIntersectNode
PortedLinearRing = PortedLinearRing
PortedLinearRingWithPolygonKind = Tuple[PortedLinearRing, PortedPolygonKind]
PortedLocalMinimum = PortedLocalMinimum
PortedLocalMinimumList = PortedLocalMinimumList
PortedMultipolygon = PortedMultipolygon
PortedOperationKind = PortedOperationKind
PortedPoint = PortedPoint
PortedPolygon = PortedPolygon
PortedPolygonKind = PortedPolygonKind
PortedRing = PortedRing
PortedRingManager = PortedRingManager
PortedWagyu = PortedWagyu

ported_edges_sides = enum_to_values(PortedEdgeSide)
ported_fill_kinds = enum_to_values(PortedFillKind)
ported_operation_kinds = enum_to_values(PortedOperationKind)
ported_polygon_kinds = enum_to_values(PortedPolygonKind)


def to_ported_linear_rings_points(raw_points: RawPointsList
                                  ) -> List[PortedPoint]:
    points = [PortedPoint(x, y) for x, y in raw_points]
    return points + [points[0]]


def to_ported_polygon_linear_rings(raw_polygon: RawPolygon
                                   ) -> List[PortedLinearRing]:
    raw_border, raw_holes = raw_polygon
    return ([PortedLinearRing(to_ported_linear_rings_points(raw_border))]
            + [PortedLinearRing(to_ported_linear_rings_points(raw_hole))
               for raw_hole in raw_holes])


def to_ported_local_minimum_list(linear_rings_with_polygon_kinds
                                 : List[PortedLinearRingWithPolygonKind]
                                 ) -> PortedLocalMinimumList:
    result = PortedLocalMinimumList()
    for linear_ring, polygon_kind in linear_rings_with_polygon_kinds:
        result.add_linear_ring(linear_ring, polygon_kind)
    return result
