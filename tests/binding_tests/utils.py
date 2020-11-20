from typing import (List,
                    Tuple)

from _wagyu import (Bound as BoundBound,
                    Box as BoundBox,
                    Edge as BoundEdge,
                    EdgeSide as BoundEdgeSide,
                    FillKind as BoundFillKind,
                    IntersectNode as BoundIntersectNode,
                    LinearRing as BoundLinearRing,
                    LocalMinimum as BoundLocalMinimum,
                    LocalMinimumList as BoundLocalMinimumList,
                    Multipolygon as BoundMultipolygon,
                    OperationKind as BoundOperationKind,
                    Point as BoundPoint,
                    Polygon as BoundPolygon,
                    PolygonKind as BoundPolygonKind,
                    Ring as BoundRing,
                    RingManager as BoundRingManager,
                    Wagyu as BoundWagyu)

from tests.utils import (RawMultipolygon,
                         RawPointsList,
                         RawPolygon,
                         enum_to_values)

BoundBound = BoundBound
BoundBox = BoundBox
BoundEdge = BoundEdge
BoundEdgeSide = BoundEdgeSide
BoundFillKind = BoundFillKind
BoundIntersectNode = BoundIntersectNode
BoundLinearRing = BoundLinearRing
BoundLinearRingWithPolygonKind = Tuple[BoundLinearRing, BoundPolygonKind]
BoundLocalMinimum = BoundLocalMinimum
BoundLocalMinimumList = BoundLocalMinimumList
BoundMultipolygon = BoundMultipolygon
BoundOperationKind = BoundOperationKind
BoundPoint = BoundPoint
BoundPolygon = BoundPolygon
BoundPolygonKind = BoundPolygonKind
BoundRing = BoundRing
BoundRingManager = BoundRingManager
BoundWagyu = BoundWagyu
bound_edges_sides = enum_to_values(BoundEdgeSide)
bound_fill_kinds = enum_to_values(BoundFillKind)
bound_operation_kinds = enum_to_values(BoundOperationKind)
bound_polygon_kinds = enum_to_values(BoundPolygonKind)


def to_bound_points_list(raw_points: RawPointsList) -> List[BoundPoint]:
    points = [BoundPoint(x, y) for x, y in raw_points]
    return points + [points[0]]


def to_bound_polygon_linear_rings(raw_polygon: RawPolygon
                                  ) -> List[BoundLinearRing]:
    raw_border, raw_holes = raw_polygon
    return ([BoundLinearRing(to_bound_points_list(raw_border))]
            + [BoundLinearRing(to_bound_points_list(raw_hole))
               for raw_hole in raw_holes])


def to_bound_local_minimum_list(linear_rings_with_polygon_kinds
                                : List[BoundLinearRingWithPolygonKind]
                                ) -> BoundLocalMinimumList:
    result = BoundLocalMinimumList()
    for linear_ring, polygon_kind in linear_rings_with_polygon_kinds:
        result.add_linear_ring(linear_ring, polygon_kind)
    return result


def to_bound_multipolygon_polygons(raw_multipolygon: RawMultipolygon
                                   ) -> List[BoundPolygon]:
    return [BoundPolygon(to_bound_polygon_linear_rings(raw_polygon))
            for raw_polygon in raw_multipolygon]
