import pickle
from enum import Enum
from functools import partial
from typing import (Callable,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple,
                    Type,
                    TypeVar)

from _wagyu import (Bound as BoundBound,
                    Box as BoundBox,
                    Edge as BoundEdge,
                    EdgeSide as BoundEdgeSide,
                    FillKind as BoundFillKind,
                    IntersectNode as BoundIntersectNode,
                    LinearRing as BoundLinearRing,
                    LocalMinimum as BoundLocalMinimum,
                    LocalMinimumList as BoundLocalMinimumList,
                    OperationKind as BoundOperationKind,
                    Point as BoundPoint,
                    Polygon as BoundPolygon,
                    PolygonKind as BoundPolygonKind,
                    Ring as BoundRing,
                    RingManager as BoundRingManager)
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from wagyu.bound import Bound as PortedBound
from wagyu.box import Box as PortedBox
from wagyu.edge import Edge as PortedEdge
from wagyu.enums import (EdgeSide as PortedEdgeSide,
                         FillKind as PortedFillKind,
                         OperationKind as PortedOperationKind,
                         PolygonKind as PortedPolygonKind)
from wagyu.hints import Coordinate
from wagyu.intersect_node import IntersectNode as PortedIntersectNode
from wagyu.linear_ring import LinearRing as PortedLinearRing
from wagyu.local_minimum import (LocalMinimum as PortedLocalMinimum,
                                 LocalMinimumList as PortedLocalMinimumList)
from wagyu.point import Point as PortedPoint
from wagyu.ring import Ring as PortedRing
from wagyu.ring_manager import RingManager as PortedRingManager

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy
RawPoint = Tuple[Coordinate, Coordinate]
RawPointsList = List[RawPoint]
RawPolygon = Tuple[RawPointsList, List[RawPointsList]]
RawMultipolygon = List[RawPolygon]

BoundBound = BoundBound
BoundBox = BoundBox
BoundEdge = BoundEdge
BoundFillKind = BoundFillKind
BoundIntersectNode = BoundIntersectNode
BoundLinearRing = BoundLinearRing
BoundLinearRingWithPolygonKind = Tuple[BoundLinearRing, BoundPolygonKind]
BoundLocalMinimum = BoundLocalMinimum
BoundLocalMinimumList = BoundLocalMinimumList
BoundOperationKind = BoundOperationKind
BoundPoint = BoundPoint
BoundPolygonKind = BoundPolygonKind
BoundRing = BoundRing
BoundRingManager = BoundRingManager

PortedBound = PortedBound
PortedBox = PortedBox
PortedEdge = PortedEdge
PortedFillKind = PortedFillKind
PortedIntersectNode = PortedIntersectNode
PortedLinearRing = PortedLinearRing
PortedLinearRingWithPolygonKind = Tuple[PortedLinearRing, PortedPolygonKind]
PortedLocalMinimum = PortedLocalMinimum
PortedLocalMinimumList = PortedLocalMinimumList
PortedOperationKind = PortedOperationKind
PortedPoint = PortedPoint
PortedPolygonKind = PortedPolygonKind
PortedRing = PortedRing
PortedRingManager = PortedRingManager

BoundPortedBoundsPair = Tuple[BoundBound, PortedBound]
BoundPortedBoundsListsPair = Tuple[List[BoundBound], List[PortedBound]]
BoundPortedBoxesPair = Tuple[BoundBox, PortedBox]
BoundPortedEdgesPair = Tuple[BoundEdge, PortedEdge]
BoundPortedEdgesListsPair = Tuple[List[BoundEdge], List[PortedEdge]]
BoundPortedEdgesSidesPair = Tuple[BoundEdgeSide, PortedEdgeSide]
BoundPortedFillKindsPair = Tuple[BoundFillKind, PortedFillKind]
BoundPortedIntersectNodesPair = Tuple[BoundIntersectNode, PortedIntersectNode]
BoundPortedLinearRingsPair = Tuple[BoundLinearRing, PortedLinearRing]
BoundPortedLocalMinimumListsPair = Tuple[BoundLocalMinimumList,
                                         PortedLocalMinimumList]
BoundPortedLocalMinimumsPair = Tuple[BoundLocalMinimum, PortedLocalMinimum]
BoundPortedLinearRingsWithPolygonsKindsListsPair = Tuple[
    List[BoundLinearRingWithPolygonKind],
    List[PortedLinearRingWithPolygonKind]]
BoundPortedMaybeRingsPair = Tuple[Optional[BoundRing], Optional[PortedRing]]
BoundPortedMaybeRingsListsPair = Tuple[List[Optional[BoundRing]],
                                       List[Optional[PortedRing]]]
BoundPortedOperationKindsPair = Tuple[BoundOperationKind, PortedOperationKind]
BoundPortedPointsPair = Tuple[BoundPoint, PortedPoint]
BoundPortedPointsListsPair = Tuple[List[BoundPoint], List[PortedPoint]]
BoundPortedPolygonKindsPair = Tuple[BoundPolygonKind, PortedPolygonKind]
BoundPortedRingManagersPair = Tuple[BoundRingManager, PortedRingManager]
BoundPortedRingsListsPair = Tuple[List[BoundRing], List[PortedRing]]
BoundPortedRingsPair = Tuple[BoundRing, PortedRing]


def enum_to_values(cls: Type[Enum]) -> List[Enum]:
    return [value for _, value in sorted(cls.__members__.items())]


bound_edges_sides = enum_to_values(BoundEdgeSide)
bound_fill_kinds = enum_to_values(BoundFillKind)
bound_operation_kinds = enum_to_values(BoundOperationKind)
bound_polygon_kinds = enum_to_values(BoundPolygonKind)
ported_edges_sides = enum_to_values(PortedEdgeSide)
ported_fill_kinds = enum_to_values(PortedFillKind)
ported_operation_kinds = enum_to_values(BoundOperationKind)
ported_polygon_kinds = enum_to_values(PortedPolygonKind)


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def transpose_pairs(pairs: List[Tuple[Domain, Range]]
                    ) -> Tuple[List[Domain], List[Range]]:
    return tuple(map(list, zip(*pairs))) if pairs else ([], [])


def pack(function: Callable[..., Range]
         ) -> Callable[[Iterable[Domain]], Range]:
    return partial(apply, function)


def apply(function: Callable[..., Range],
          args: Iterable[Domain]) -> Range:
    return function(*args)


def sort_pair(pair: Tuple[Domain, Domain]) -> Tuple[Domain, Domain]:
    first, second = pair
    return pair if first < second else (second, first)


def pickle_round_trip(object_: Domain) -> Domain:
    return pickle.loads(pickle.dumps(object_))


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_maybe(strategy: Strategy[Domain]) -> Strategy[Optional[Domain]]:
    return strategies.none() | strategy


def to_maybe_pairs(strategy: Strategy[Tuple[Domain, Range]]
                   ) -> Strategy[Tuple[Optional[Domain], Optional[Range]]]:
    return to_pairs(strategies.none()) | strategy


def subsequences(sequence: Sequence) -> SearchStrategy[Sequence]:
    return strategies.builds(sequence.__getitem__,
                             strategies.slices(max(len(sequence), 1)))


def to_maybe_equals(equals: Callable[[Domain, Range], bool]
                    ) -> Callable[[Optional[Domain], Optional[Range]], bool]:
    def maybe_equals(left: Optional[Domain], right: Optional[Range]) -> bool:
        return ((left is None) is (right is None)
                and (left is None or equals(left, right)))

    return maybe_equals


def to_sequences_equals(equals: Callable[[Domain, Range], bool]
                        ) -> Callable[[Sequence[Domain], Sequence[Range]],
                                      bool]:
    def sequences_equals(left: Sequence[Domain],
                         right: Sequence[Range]) -> bool:
        return len(left) == len(right) and all(map(equals, left, right))

    return sequences_equals


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


def are_bound_ported_local_minimums_equal(bound: BoundLocalMinimum,
                                          ported: PortedLocalMinimum) -> bool:
    return (are_bound_ported_bounds_equal(bound.left_bound, ported.left_bound)
            and are_bound_ported_bounds_equal(bound.right_bound,
                                              ported.right_bound)
            and bound.y == ported.y
            and bound.minimum_has_horizontal is ported.minimum_has_horizontal)


are_bound_ported_local_minimums_lists_equal = to_sequences_equals(
        are_bound_ported_local_minimums_equal)


def are_bound_ported_bounds_equal(bound: BoundBound,
                                  ported: PortedBound) -> bool:
    return (are_bound_ported_plain_bounds_lists_equal(
            list(traverse_bound(bound)), list(traverse_bound(ported)))
            and bound.current_edge_index == ported.current_edge_index
            and bound.next_edge_index == ported.next_edge_index)


are_bound_ported_maybe_bounds_equal = to_maybe_equals(
        are_bound_ported_bounds_equal)
are_bound_ported_bounds_lists_equal = to_sequences_equals(
        are_bound_ported_bounds_equal)
are_bound_ported_maybe_bounds_lists_equal = to_sequences_equals(
        are_bound_ported_maybe_bounds_equal)

AnyBound = TypeVar('AnyBound', BoundBound, PortedBound)


def traverse_bound(bound: AnyBound) -> Iterable[AnyBound]:
    seen_ids = set()
    cursor = bound
    while cursor is not None and id(cursor) not in seen_ids:
        yield cursor
        seen_ids.add(id(cursor))
        cursor = cursor.maximum_bound


def are_bound_ported_plain_bounds_equal(bound: BoundBound,
                                        ported: PortedBound) -> bool:
    return (are_bound_ported_edges_lists_equal(bound.edges, ported.edges)
            and are_bound_ported_points_equal(bound.last_point,
                                              ported.last_point)
            and are_bound_ported_maybe_rings_equal(bound.ring, ported.ring)
            and bound.current_x == ported.current_x
            and bound.position == ported.position
            and bound.winding_count == ported.winding_count
            and bound.opposite_winding_count == ported.opposite_winding_count
            and bound.winding_delta == ported.winding_delta
            and bound.polygon_kind == ported.polygon_kind
            and bound.side == ported.side)


are_bound_ported_plain_bounds_lists_equal = to_sequences_equals(
        are_bound_ported_plain_bounds_equal)
are_bound_ported_maybe_bounds_equal = to_maybe_equals(
        are_bound_ported_bounds_equal)


def are_bound_ported_edges_lists_equal(bound: List[BoundEdge],
                                       ported: List[PortedEdge]) -> bool:
    return (len(bound) == len(ported)
            and all(map(are_bound_ported_edges_equal, bound, ported)))


def are_bound_ported_intersect_nodes_equal(bound: BoundIntersectNode,
                                           ported: PortedIntersectNode
                                           ) -> bool:
    return (are_bound_ported_bounds_equal(bound.first_bound,
                                          ported.first_bound)
            and are_bound_ported_bounds_equal(bound.second_bound,
                                              ported.second_bound)
            and are_bound_ported_points_equal(bound.point, ported.point))


are_bound_ported_intersect_nodes_lists_equal = to_sequences_equals(
        are_bound_ported_intersect_nodes_equal)


def are_bound_ported_points_equal(bound: BoundPoint,
                                  ported: PortedPoint) -> bool:
    return bound.x == ported.x and bound.y == ported.y


are_bound_ported_maybe_points_equal = to_maybe_equals(
        are_bound_ported_points_equal)
are_bound_ported_points_lists_equal = to_sequences_equals(
        are_bound_ported_points_equal)
are_bound_ported_points_lists_lists_equal = to_sequences_equals(
        are_bound_ported_points_lists_equal)


def are_bound_ported_rings_equal(bound: BoundRing,
                                 ported: PortedRing) -> bool:
    return (bound.index == ported.index
            and are_bound_ported_maybe_rings_lists_equal(bound.children,
                                                         ported.children)
            and are_bound_ported_points_lists_equal(bound.points,
                                                    ported.points)
            and are_bound_ported_points_lists_equal(bound.bottom_points,
                                                    ported.bottom_points)
            and bound.corrected is ported.corrected)


are_bound_ported_maybe_rings_equal = to_maybe_equals(
        are_bound_ported_rings_equal)
are_bound_ported_rings_lists_equal = to_sequences_equals(
        are_bound_ported_rings_equal)
are_bound_ported_maybe_rings_lists_equal = to_sequences_equals(
        are_bound_ported_maybe_rings_equal)


def are_bound_ported_ring_managers_equal(bound: BoundRingManager,
                                         ported: PortedRingManager) -> bool:
    return (are_bound_ported_maybe_rings_lists_equal(bound.children,
                                                     ported.children)
            and are_bound_ported_points_lists_equal(bound.hot_pixels,
                                                    ported.hot_pixels)
            and are_bound_ported_points_lists_lists_equal(bound.points,
                                                          ported.points)
            and are_bound_ported_rings_lists_equal(bound.rings, ported.rings)
            and are_bound_ported_points_lists_lists_equal(bound.stored_points,
                                                          ported.stored_points)
            and bound.index == ported.index)


def to_bound_with_ported_bounds_pair(edges: BoundPortedEdgesListsPair,
                                     current_edge_index: int,
                                     next_edge_index: int,
                                     last_points_pair: BoundPortedPointsPair,
                                     rings_pair
                                     : BoundPortedMaybeRingsListsPair,
                                     current_x: float,
                                     position: int,
                                     winding_count: int,
                                     opposite_winding_count: int,
                                     winding_delta: int,
                                     polygon_kinds_pair
                                     : BoundPortedPolygonKindsPair,
                                     sides_pair: BoundPortedEdgesSidesPair
                                     ) -> BoundPortedBoundsPair:
    bound_edges, ported_edges = edges
    bound_last_point, ported_last_point = last_points_pair
    bound_ring, ported_ring = rings_pair
    bound_polygon_kind, ported_polygon_kind = polygon_kinds_pair
    bound_edge_side, ported_edge_side = sides_pair
    return (BoundBound(bound_edges, current_edge_index, next_edge_index,
                       bound_last_point, bound_ring, current_x, position,
                       winding_count, opposite_winding_count, winding_delta,
                       bound_polygon_kind, bound_edge_side),
            PortedBound(ported_edges, current_edge_index, next_edge_index,
                        ported_last_point, ported_ring, current_x, position,
                        winding_count, opposite_winding_count, winding_delta,
                        ported_polygon_kind, ported_edge_side))


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


def to_bound_with_ported_edges_lists(linear_rings: BoundPortedLinearRingsPair
                                     ) -> BoundPortedEdgesListsPair:
    bound_linear_ring, ported_linear_ring = linear_rings
    return bound_linear_ring.edges, ported_linear_ring.edges


def to_bound_with_ported_intersect_nodes_pair(
        first_bounds_pair: BoundPortedBoundsPair,
        second_bounds_pair: BoundPortedBoundsPair,
        points_pair: BoundPortedPointsPair) -> BoundPortedIntersectNodesPair:
    bound_first_bound, ported_first_bound = first_bounds_pair
    bound_second_bound, ported_second_bound = second_bounds_pair
    bound_point, ported_point = points_pair
    return (BoundIntersectNode(bound_first_bound, bound_second_bound,
                               bound_point),
            PortedIntersectNode(ported_first_bound, ported_second_bound,
                                ported_point))


def to_bound_with_ported_linear_rings_points(raw_points: RawPointsList
                                             ) -> BoundPortedPointsListsPair:
    return (to_bound_linear_rings_points(raw_points),
            to_ported_linear_rings_points(raw_points))


def to_bound_with_ported_linear_rings(linear_rings_points
                                      : BoundPortedPointsListsPair
                                      ) -> BoundPortedLinearRingsPair:
    bound_points, ported_points = linear_rings_points
    return BoundLinearRing(bound_points), PortedLinearRing(ported_points)


def to_bound_with_ported_local_minimum_lists(
        rings_with_kinds: BoundPortedLinearRingsWithPolygonsKindsListsPair
) -> BoundPortedLocalMinimumListsPair:
    bound_rings_with_kinds, ported_rings_with_kinds = rings_with_kinds
    return (to_bound_local_minimum_list(bound_rings_with_kinds),
            to_ported_local_minimum_list(ported_rings_with_kinds))


def to_bound_with_ported_rings_pair(index: int,
                                    children_pair
                                    : BoundPortedMaybeRingsListsPair,
                                    points_pair: BoundPortedPointsListsPair,
                                    corrected: bool) -> BoundPortedRingsPair:
    bound_children, ported_children = children_pair
    bound_points, ported_points = points_pair
    return (BoundRing(index, bound_children, bound_points, corrected),
            PortedRing(index, ported_children, ported_points, corrected))


def to_bound_with_ported_ring_managers_pair(
        children_pair: BoundPortedMaybeRingsListsPair,
        hot_pixels_pair: BoundPortedPointsListsPair,
        current_hot_pixel_index: int,
        rings_pair: BoundPortedMaybeRingsListsPair,
        index: int) -> BoundPortedRingManagersPair:
    bound_children, ported_children = children_pair
    bound_hot_pixels, ported_hot_pixels = hot_pixels_pair
    bound_rings, ported_rings = rings_pair
    return (BoundRingManager(bound_children, bound_hot_pixels,
                             current_hot_pixel_index, bound_rings, index),
            PortedRingManager(ported_children, ported_hot_pixels,
                              current_hot_pixel_index, ported_rings, index))


def to_bound_with_ported_points_pair(x: float, y: float
                                     ) -> BoundPortedPointsPair:
    return BoundPoint(x, y), PortedPoint(x, y)


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


def to_ported_linear_rings_points(raw_points: RawPointsList
                                  ) -> List[PortedPoint]:
    points = [PortedPoint(x, y) for x, y in raw_points]
    return points + [points[0]]


def to_ported_local_minimum_list(linear_rings_with_polygon_kinds
                                 : List[PortedLinearRingWithPolygonKind]
                                 ) -> PortedLocalMinimumList:
    result = PortedLocalMinimumList()
    for linear_ring, polygon_kind in linear_rings_with_polygon_kinds:
        result.add_linear_ring(linear_ring, polygon_kind)
    return result


def to_ported_polygon_linear_rings(raw_polygon: RawPolygon
                                   ) -> List[PortedLinearRing]:
    raw_border, raw_holes = raw_polygon
    return ([PortedLinearRing(to_ported_linear_rings_points(raw_border))]
            + [PortedLinearRing(to_ported_linear_rings_points(raw_hole))
               for raw_hole in raw_holes])


def initialize_bounds(bounds_pair: BoundPortedBoundsPair,
                      edges_indices: Tuple[int, int]) -> BoundPortedBoundsPair:
    bound, ported = bounds_pair
    bound.current_edge_index, bound.next_edge_index = edges_indices
    ported.current_edge_index, ported.next_edge_index = edges_indices
    return bounds_pair
