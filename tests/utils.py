import pickle
from functools import partial
from itertools import zip_longest
from typing import (Callable,
                    Iterable,
                    List,
                    Optional,
                    Tuple,
                    TypeVar)

from _wagyu import (Box as BoundBox,
                    Edge as BoundEdge,
                    LinearRing as BoundLinearRing,
                    Point as BoundPoint,
                    PointNode as BoundPointNode,
                    Polygon as BoundPolygon)
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from wagyu.box import Box as PortedBox
from wagyu.edge import Edge as PortedEdge
from wagyu.hints import Coordinate
from wagyu.point import Point as PortedPoint
from wagyu.point_node import PointNode as PortedPointNode

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy
RawPoint = Tuple[Coordinate, Coordinate]
RawPointsList = List[RawPoint]
RawPolygon = Tuple[RawPointsList, List[RawPointsList]]
RawMultipolygon = List[RawPolygon]
BoundBox = BoundBox
BoundEdge = BoundEdge
BoundPoint = BoundPoint
BoundPointNode = BoundPointNode
BoundPortedBoxesPair = Tuple[BoundBox, PortedBox]
BoundPortedEdgesPair = Tuple[BoundEdge, PortedEdge]
BoundPortedPointsPair = Tuple[BoundPoint, PortedPoint]
BoundPortedPointsNodesPair = Tuple[BoundPointNode, PortedPointNode]
PortedBox = PortedBox
PortedEdge = PortedEdge
PortedPoint = PortedPoint
PortedPointNode = PortedPointNode


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def pack(function: Callable[..., Range]
         ) -> Callable[[Iterable[Domain]], Range]:
    return partial(apply, function)


def apply(function: Callable[..., Range],
          args: Iterable[Domain]) -> Range:
    return function(*args)


def pickle_round_trip(object_: Domain) -> Domain:
    return pickle.loads(pickle.dumps(object_))


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_maybe(strategy: Strategy[Domain]) -> Strategy[Optional[Domain]]:
    return strategies.none() | strategy


def are_endpoints_non_degenerate(endpoints: Tuple[BoundPortedPointsPair,
                                                  BoundPortedPointsPair]
                                 ) -> bool:
    (first_bound, _), (second_bound, _) = endpoints
    return first_bound != second_bound


def are_bound_ported_boxes_equal(bound: BoundBox, ported: PortedBox) -> bool:
    return (are_bound_ported_points_equal(bound.minimum, ported.minimum)
            and are_bound_ported_points_equal(bound.maximum, ported.maximum))


def are_bound_ported_edges_equal(bound: BoundEdge, ported: PortedEdge) -> bool:
    return (are_bound_ported_points_equal(bound.top, ported.top)
            and are_bound_ported_points_equal(bound.bottom, ported.bottom))


def are_bound_ported_points_equal(bound: BoundPoint,
                                  ported: PortedPoint) -> bool:
    return bound.x == ported.x and bound.y == ported.y


def are_bound_ported_points_nodes_equal(bound: BoundPointNode,
                                        ported: PortedPointNode) -> bool:
    return all(
            bound_node is not None
            and ported_node is not None
            and bound_node.x == ported_node.x
            and bound_node.y == ported_node.y
            for bound_node, ported_node in zip_longest(traverse_tree(bound),
                                                       traverse_tree(ported),
                                                       fillvalue=None))


AnyPointNode = TypeVar('AnyPointNode', BoundPointNode, PortedPointNode)


def traverse_tree(point_node: AnyPointNode) -> Iterable[AnyPointNode]:
    cursor = point_node
    while True:
        yield cursor
        cursor = cursor.next
        if cursor is point_node:
            break


def to_bound_with_ported_boxes_pair(minimums: BoundPortedPointsPair,
                                    maximums: BoundPortedPointsPair
                                    ) -> BoundPortedBoxesPair:
    bound_minimum, ported_minimum = minimums
    bound_maximum, ported_maximum = maximums
    return (BoundBox(bound_minimum, bound_maximum),
            PortedBox(ported_minimum, ported_maximum))


def to_bound_with_ported_edges_pair(starts: BoundPortedPointsPair,
                                    ends: BoundPortedPointsPair
                                    ) -> BoundPortedEdgesPair:
    bound_start, ported_start = starts
    bound_end, ported_end = ends
    return BoundEdge(bound_start, bound_end), PortedEdge(ported_start,
                                                         ported_end)


def to_bound_with_ported_points_pair(x: float, y: float
                                     ) -> BoundPortedPointsPair:
    return BoundPoint(x, y), PortedPoint(x, y)


def to_bound_with_ported_points_nodes_pair(x: float, y: float
                                           ) -> BoundPortedPointsNodesPair:
    return BoundPointNode(x, y), PortedPointNode(x, y)


def to_bound_linear_rings_points(raw_points: RawPointsList
                                 ) -> List[BoundPoint]:
    points = [BoundPoint(x, y) for x, y in raw_points]
    return points + [points[0]]


def to_bound_polygon_linear_rings(raw_polygon: RawPolygon
                                  ) -> List[BoundLinearRing]:
    raw_border, raw_holes = raw_polygon
    return ([BoundLinearRing(to_bound_linear_rings_points(raw_border))]
            + [BoundLinearRing(to_bound_linear_rings_points(raw_hole))
               for raw_hole in raw_holes])


def to_bound_multipolygon_polygons(raw_multipolygon: RawMultipolygon
                                   ) -> List[BoundPolygon]:
    return [BoundPolygon(to_bound_polygon_linear_rings(raw_polygon))
            for raw_polygon in raw_multipolygon]
