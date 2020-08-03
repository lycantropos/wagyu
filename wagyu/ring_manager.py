import math
from functools import partial
from itertools import groupby
from operator import is_not
from typing import (List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from .bound import (Bound,
                    insert_bound_into_abl,
                    intersection_compare,
                    set_winding_count)
from .bubble_sort import bubble_sort
from .enums import (EdgeSide,
                    FillKind,
                    OperationKind,
                    PolygonKind)
from .hints import Coordinate
from .intersect_node import (IntersectNode,
                             build_intersect_list)
from .local_minimum import (LocalMinimum,
                            LocalMinimumList)
from .point import Point
from .point_node import (PointNode,
                         maybe_point_node_to_points,
                         point_node_to_point)
from .polygon import Multipolygon
from .ring import (Ring,
                   remove_from_children,
                   set_to_children)
from .utils import (are_floats_greater_than,
                    are_floats_less_than,
                    find,
                    find_if,
                    insort_unique,
                    is_odd,
                    quicksort,
                    round_half_up)


class RingManager:
    __slots__ = ('children', 'all_nodes', 'hot_pixels',
                 '_current_hot_pixel_index',
                 'nodes', 'rings', 'storage', 'index')

    def __init__(self,
                 children: Optional[List[Optional[Ring]]] = None,
                 hot_pixels: Optional[List[Point]] = None,
                 current_hot_pixel_index: Optional[int] = None,
                 rings: Optional[List[Ring]] = None,
                 index: int = 0) -> None:
        self.children = [] if children is None else children
        self.hot_pixels = [] if hot_pixels is None else hot_pixels
        self._current_hot_pixel_index = (
            None
            if (current_hot_pixel_index is None
                or current_hot_pixel_index >= len(self.hot_pixels))
            else current_hot_pixel_index)
        self.rings = [] if rings is None else rings
        self.index = index
        self.all_nodes = []  # type: List[Optional[PointNode]]
        self.nodes = []  # type: List[PointNode]
        self.storage = []  # type: List[PointNode]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'RingManager') -> bool:
        return (self.children == other.children
                and self.all_nodes == other.all_nodes
                and self.hot_pixels == other.hot_pixels
                and (self.current_hot_pixel_index
                     == other.current_hot_pixel_index)
                and self.nodes == other.nodes
                and self.rings == other.rings
                and self.storage == other.storage
                and self.index == other.index
                if isinstance(other, RingManager)
                else NotImplemented)

    @property
    def all_points(self) -> List[List[Point]]:
        return [maybe_point_node_to_points(node) for node in self.all_nodes]

    @property
    def current_hot_pixel_index(self) -> int:
        return (len(self.hot_pixels)
                if (self._current_hot_pixel_index is None
                    or self._current_hot_pixel_index >= len(self.hot_pixels))
                else self._current_hot_pixel_index)

    @current_hot_pixel_index.setter
    def current_hot_pixel_index(self, value: int) -> None:
        self._current_hot_pixel_index = (value
                                         if value < len(self.hot_pixels)
                                         else None)

    @property
    def points(self) -> List[List[Point]]:
        return [list(map(point_node_to_point, node)) for node in self.nodes]

    @property
    def stored_points(self) -> List[List[Point]]:
        return [list(map(point_node_to_point, node)) for node in self.storage]

    def add_first_point(self, bound: Bound, active_bounds: List[Bound],
                        point: Point) -> None:
        ring = bound.ring = self.create_ring()
        ring.node = self.create_point_node(ring, point)
        self.set_hole_state(bound, active_bounds)
        bound.last_point = point

    def add_local_maximum_point(self,
                                point: Point,
                                first_bound: Bound,
                                second_bound: Bound,
                                active_bounds: List[Bound]) -> None:
        self.insert_hot_pixels_in_path(second_bound, point, False)
        self.add_point(first_bound, active_bounds, point)
        if first_bound.ring is second_bound.ring:
            first_bound.ring = None
            second_bound.ring = None
            # I am not certain that order is important here?
        elif first_bound.ring.index < second_bound.ring.index:
            self.append_ring(first_bound, second_bound, active_bounds)
        else:
            self.append_ring(second_bound, first_bound, active_bounds)

    def add_local_minimum_point(self,
                                point: Point,
                                first_bound: Bound,
                                second_bound: Bound,
                                active_bounds: List[Bound]) -> None:
        if (second_bound.current_edge.is_horizontal
                or (first_bound.current_edge.slope
                    > second_bound.current_edge.slope)):
            self.add_point(first_bound, active_bounds, point)
            second_bound.last_point = point
            second_bound.ring = first_bound.ring
            first_bound.side = EdgeSide.LEFT
            second_bound.side = EdgeSide.RIGHT
        else:
            self.add_point(second_bound, active_bounds, point)
            first_bound.last_point = point
            first_bound.ring = second_bound.ring
            first_bound.side = EdgeSide.RIGHT
            second_bound.side = EdgeSide.LEFT

    def add_point(self, bound: Bound, active_bounds: List[Bound],
                  point: Point) -> None:
        if bound.ring is None:
            self.add_first_point(bound, active_bounds, point)
        else:
            self.add_point_to_ring(bound, point)

    def add_point_to_ring(self, bound: Bound, point: Point) -> None:
        assert bound.ring is not None
        # handle hot pixels
        self.insert_hot_pixels_in_path(bound, point, False)
        # ``bound.ring.node`` is the 'leftmost' point,
        # ``bound.ring.node.prev`` is the 'rightmost'
        op = bound.ring.node
        to_front = bound.side is EdgeSide.LEFT
        if to_front and point == op or (not to_front and (point == op.prev)):
            return
        new_node = self.create_point_node(bound.ring, point, op)
        if to_front:
            bound.ring.node = new_node

    def append_ring(self, first_bound: Bound, second_bound: Bound,
                    active_bounds: List[Bound]) -> None:
        # get the start and ends of both output polygons
        first_out_rec = first_bound.ring
        second_out_rec = second_bound.ring
        if first_out_rec.is_descendant_of(second_out_rec):
            keep_ring, remove_ring = second_out_rec, first_out_rec
            keep_bound, remove_bound = second_bound, first_bound
        elif second_out_rec.is_descendant_of(first_out_rec):
            keep_ring, remove_ring = first_out_rec, second_out_rec
            keep_bound, remove_bound = first_bound, second_bound
        elif first_out_rec is first_out_rec.get_lowermost_ring(second_out_rec):
            keep_ring, remove_ring = first_out_rec, second_out_rec
            keep_bound, remove_bound = first_bound, second_bound
        else:
            keep_ring, remove_ring = second_out_rec, first_out_rec
            keep_bound, remove_bound = second_bound, first_bound
        # get the start and ends of both output polygons and
        # join second bound's polygon onto first bound's polygon
        # and delete pointers to second bound
        p1_lft = keep_ring.node
        p1_rt = p1_lft.prev
        p2_lft = remove_ring.node
        p2_rt = p2_lft.prev
        # join second bound's polygon onto first bound's polygon
        # and delete pointers to second bound
        if keep_bound.side is EdgeSide.LEFT:
            if remove_bound.side is EdgeSide.LEFT:
                # z y x a b c
                p2_lft.reverse()
                p2_lft.next = p1_lft
                p1_lft.prev = p2_lft
                p1_rt.next = p2_rt
                p2_rt.prev = p1_rt
                keep_ring.node = p2_rt
            else:
                # x y z a b c
                p2_rt.next = p1_lft
                p1_lft.prev = p2_rt
                p2_lft.prev = p1_rt
                p1_rt.next = p2_lft
                keep_ring.node = p2_lft
        else:
            if remove_bound.side is EdgeSide.RIGHT:
                # a b c z y x
                p2_lft.reverse()
                p1_rt.next = p2_rt
                p2_rt.prev = p1_rt
                p2_lft.next = p1_lft
                p1_lft.prev = p2_lft
            else:
                # a b c x y z
                p1_rt.next = p2_lft
                p2_lft.prev = p1_rt
                p1_lft.prev = p2_rt
                p2_rt.next = p1_lft
        keep_ring.bottom_node = None
        keep_is_hole = is_odd(keep_ring.depth)
        remove_is_hole = is_odd(remove_ring.depth)
        if keep_is_hole is not remove_is_hole:
            self.replace_ring(keep_ring.parent, remove_ring)
        else:
            self.replace_ring(keep_ring, remove_ring)
        keep_ring.update_points()
        remove_bound.ring = keep_bound.ring = None
        for bound in active_bounds:
            if bound is None:
                continue
            if bound.ring is remove_ring:
                bound.ring = keep_ring
                bound.side = keep_bound.side
                # not sure why there is a break here but was transferred logic
                # from angus
                break

    def build_hot_pixels(self, minimums: LocalMinimumList) -> None:
        sorted_minimums = sorted(minimums,
                                 reverse=True)
        minimums_index = 0
        scanbeams = minimums.scanbeams
        active_bounds = []  # type: List[Optional[Bound]]
        scanline_y = math.inf
        while scanbeams or minimums_index < len(minimums):
            try:
                scanline_y = scanbeams.pop()
            except IndexError:
                pass
            active_bounds = self.process_hot_pixel_intersections(scanline_y,
                                                                 active_bounds)
            minimums_index = self.insert_local_minima_into_abl_hot_pixel(
                    scanline_y, sorted_minimums, minimums_index, active_bounds,
                    scanbeams)
            active_bounds = self.process_hot_pixel_edges_at_top_of_scanbeam(
                    scanline_y, scanbeams, active_bounds)
        self.sort_hot_pixels()

    def build_result(self, reverse_output: bool) -> Multipolygon:
        return Multipolygon.from_rings(self.rings, reverse_output)

    def correct_orientations(self) -> None:
        for ring in self.rings:
            if ring.node is None:
                continue
            ring.recalculate_stats()
            if ring.size < 3:
                self.remove_ring_and_points(ring, False)
                continue
            if is_odd(ring.depth) is not ring.is_hole:
                ring.node.reverse()
                ring.recalculate_stats()

    def correct_self_intersection(self,
                                  first_node: PointNode,
                                  second_node: PointNode) -> Optional[Ring]:
        if first_node.ring is not second_node.ring:
            return None
        ring = first_node.ring
        # split the polygon into two
        third_node = first_node.prev
        fourth_node = second_node.prev
        first_node.prev = fourth_node
        fourth_node.next = first_node
        second_node.prev = third_node
        third_node.next = second_node
        result = self.create_ring()
        first_area, first_size, first_box = first_node.stats
        second_area, second_size, second_box = second_node.stats
        if abs(first_area) > abs(second_area):
            ring.node = first_node
            ring.set_stats(first_area, first_size, first_box)
            result.node = second_node
            result.set_stats(second_area, second_size, second_box)
        else:
            ring.node = second_node
            ring.set_stats(second_area, second_size, second_box)
            result.node = first_node
            result.set_stats(first_area, first_size, first_box)
        result.update_points()
        return result

    def create_point_node(self, ring: Optional[Ring], point: Point,
                          before_this_point: Optional[PointNode] = None
                          ) -> PointNode:
        result = PointNode(point.x, point.y)
        result.ring = ring
        if before_this_point is not None:
            result.place_before(before_this_point)
        self.nodes.append(result)
        self.all_nodes.append(result)
        return result

    def create_ring(self) -> Ring:
        result = Ring(self.index)
        self.index += 1
        self.rings.append(result)
        return result

    def do_maxima(self,
                  operation_kind: OperationKind,
                  subject_fill_kind: FillKind,
                  clip_fill_kind: FillKind,
                  bound_index: int,
                  bound_maximum_index: int,
                  active_bounds: List[Bound]) -> int:
        next_bound_index = bound_index + 1
        result = bound_index
        skipped = False
        while (next_bound_index < len(active_bounds)
               and next_bound_index != bound_maximum_index):
            if active_bounds[next_bound_index] is None:
                next_bound_index += 1
                continue
            skipped = True
            bound = active_bounds[bound_index]
            self.intersect_bounds(bound.current_edge.top, operation_kind,
                                  subject_fill_kind, clip_fill_kind, bound,
                                  active_bounds[next_bound_index],
                                  active_bounds)
            active_bounds[bound_index], active_bounds[next_bound_index] = (
                active_bounds[next_bound_index], active_bounds[bound_index])
            bound_index = next_bound_index
            next_bound_index += 1
        if (active_bounds[bound_index].ring is not None
                and active_bounds[bound_maximum_index].ring is not None):
            bound = active_bounds[bound_index]
            self.add_local_maximum_point(bound.current_edge.top, bound,
                                         active_bounds[bound_maximum_index],
                                         active_bounds)
        elif (active_bounds[bound_index].ring is not None
              or active_bounds[bound_maximum_index].ring is not None):
            raise RuntimeError("DoMaxima error")
        active_bounds[bound_index] = active_bounds[bound_maximum_index] = None
        return result + (not skipped)

    def execute_vatti(self,
                      minimums: LocalMinimumList,
                      operation_kind: OperationKind,
                      subject_fill_kind: FillKind,
                      clip_fill_kind: FillKind) -> None:
        sorted_minimums = sorted(minimums,
                                 reverse=True)
        scanbeams = minimums.scanbeams
        active_bounds = []  # type: List[Optional[Bound]]
        self.current_hot_pixel_index = 0
        minimums_index = 0
        scanline_y = math.inf
        while scanbeams or minimums_index < len(minimums):
            try:
                scanline_y = scanbeams.pop()
            except IndexError:
                pass
            self.process_intersections(scanline_y, operation_kind,
                                       subject_fill_kind, clip_fill_kind,
                                       active_bounds)
            while (self.hot_pixels[self.current_hot_pixel_index].y
                   > scanline_y):
                self.current_hot_pixel_index += 1
            # first we process bounds that has already been added
            # to the active bound list -- if the active bound list is empty
            # local minima that are at this scanline_y and have
            # a horizontal edge at the local minima will be processed
            active_bounds, minimums_index = (
                self.process_edges_at_top_of_scanbeam(
                        operation_kind, subject_fill_kind, clip_fill_kind,
                        scanline_y, scanbeams, active_bounds, minimums_index,
                        sorted_minimums))
            # next we will add local minima bounds to the active bounds list
            # that are on the local minima queue at this current scanline_y
            minimums_index = self.insert_local_minima_into_abl(
                    operation_kind, subject_fill_kind, clip_fill_kind,
                    scanline_y, scanbeams, sorted_minimums, minimums_index,
                    active_bounds)

    def horizontals_at_top_scanbeam(self,
                                    top_y: Coordinate,
                                    active_bounds: List[Bound],
                                    current_bound_index: int
                                    ) -> Tuple[int, bool]:
        shifted = False
        current_edge = active_bounds[current_bound_index].current_edge
        active_bounds[current_bound_index].current_x = current_edge.top.x
        if current_edge.bottom.x < current_edge.top.x:
            next_bound_index = current_bound_index + 1
            while (next_bound_index < len(active_bounds)
                   and (active_bounds[next_bound_index] is None
                        or active_bounds[next_bound_index].current_x
                        < active_bounds[current_bound_index].current_x)):
                bound_next = active_bounds[next_bound_index]
                if (bound_next is not None
                        and bound_next.current_edge.top.y != top_y
                        and bound_next.current_edge.bottom.y != top_y):
                    self.hot_pixels.append(
                            Point(round_half_up(bound_next.current_x),
                                  top_y))
                (active_bounds[current_bound_index],
                 active_bounds[next_bound_index]) = (
                    active_bounds[next_bound_index],
                    active_bounds[current_bound_index])
                current_bound_index += 1
                next_bound_index += 1
                shifted = True
        elif current_bound_index > 0:
            prev_bound_index = current_bound_index - 1
            while (current_bound_index > 0
                   and (active_bounds[prev_bound_index] is None
                        or active_bounds[prev_bound_index].current_x
                        > active_bounds[current_bound_index].current_x)):
                prev_bound = active_bounds[prev_bound_index]
                if (prev_bound is not None
                        and prev_bound.current_edge.top.y != top_y
                        and prev_bound.current_edge.bottom.y != top_y):
                    self.hot_pixels.append(
                            Point(round_half_up(prev_bound.current_x),
                                  top_y))
                (active_bounds[current_bound_index],
                 active_bounds[prev_bound_index]) = (
                    active_bounds[prev_bound_index],
                    active_bounds[current_bound_index])
                current_bound_index -= 1
                prev_bound_index -= 1
        return current_bound_index, shifted

    def hot_pixels_on_swap(self,
                           first_bound: Bound,
                           second_bound: Bound) -> None:
        intersection = first_bound.current_edge & second_bound.current_edge
        if intersection is None:
            raise RuntimeError('Trying to find intersection of lines '
                               'that do not intersect')
        self.hot_pixels.append(intersection.round())

    def hot_pixel_set_left_to_right(self,
                                    y: Coordinate,
                                    start_x: Coordinate,
                                    end_x: Coordinate,
                                    bound: Bound,
                                    hot_pixel_start: int,
                                    hot_pixel_stop: int,
                                    add_end_point: bool) -> int:
        x_min = max(bound.current_edge.get_min_x(y), start_x)
        x_max = min(bound.current_edge.get_max_x(y), end_x)
        for hot_pixel_index in range(hot_pixel_start, hot_pixel_stop):
            hot_pixel = self.hot_pixels[hot_pixel_index]
            if hot_pixel.x < x_min:
                continue
            elif hot_pixel.x > x_max:
                break
            if not add_end_point and hot_pixel.x == end_x:
                continue
            op = bound.ring.node
            to_front = bound.side is EdgeSide.LEFT
            if to_front and hot_pixel == op:
                continue
            elif not to_front and hot_pixel == op.prev:
                continue
            new_node = self.create_point_node(bound.ring, hot_pixel, op)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_stop
        return hot_pixel_index

    def hot_pixel_set_right_to_left(self,
                                    y: Coordinate,
                                    start_x: Coordinate,
                                    end_x: Coordinate,
                                    bound: Bound,
                                    hot_pixel_start: int,
                                    hot_pixel_stop: int,
                                    add_end_point: bool) -> int:
        x_min = max(bound.current_edge.get_min_x(y), end_x)
        x_max = min(bound.current_edge.get_max_x(y), start_x)
        for hot_pixel_index in reversed(range(hot_pixel_start,
                                              hot_pixel_stop)):
            hot_pixel = self.hot_pixels[hot_pixel_index]
            if hot_pixel.x > x_max:
                continue
            elif hot_pixel.x < x_min:
                break
            if not add_end_point and hot_pixel.x == end_x:
                continue
            op = bound.ring.node
            to_front = bound.side is EdgeSide.LEFT
            if to_front and hot_pixel == op:
                continue
            elif not to_front and hot_pixel == op.prev:
                continue
            new_node = self.create_point_node(bound.ring, hot_pixel, op)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_start - 1
        return hot_pixel_index

    def insert_horizontal_local_minima_into_abl(self,
                                                operation_kind: OperationKind,
                                                subject_fill_kind: FillKind,
                                                clip_fill_kind: FillKind,
                                                top_y: Coordinate,
                                                scanbeams: List[Coordinate],
                                                minimums: LocalMinimumList,
                                                minimums_index: int,
                                                active_bounds: List[Bound]
                                                ) -> int:
        while (minimums_index < len(minimums)
               and minimums[minimums_index].y == top_y
               and minimums[minimums_index].minimum_has_horizontal):
            minimum = minimums[minimums_index]
            minimum.initialize()
            self.insert_lm_left_and_right_bound(
                    operation_kind, subject_fill_kind, clip_fill_kind,
                    scanbeams, minimum.left_bound, minimum.right_bound,
                    active_bounds)
            minimums_index += 1
        return minimums_index

    def insert_hot_pixels_in_path(self,
                                  bound: Bound,
                                  end_point: Point,
                                  add_end_point: bool) -> None:
        if end_point == bound.last_point:
            return
        start_x, start_y = bound.last_point.x, bound.last_point.y
        end_x, end_y = end_point.x, end_point.y
        index = self.current_hot_pixel_index
        while self.hot_pixels[index].y <= start_y and index > 0:
            index -= 1
        if start_x > end_x:
            while index < len(self.hot_pixels):
                y = self.hot_pixels[index].y
                if y > start_y:
                    index += 1
                    continue
                elif y < end_y:
                    break
                first_index = index
                while (index < len(self.hot_pixels)
                       and self.hot_pixels[index].y == y):
                    index += 1
                last_index = index
                self.hot_pixel_set_right_to_left(
                        y, start_x, end_x, bound, first_index, last_index,
                        y != end_point.y or add_end_point)
        else:
            while index < len(self.hot_pixels):
                y = self.hot_pixels[index].y
                if y > start_y:
                    index += 1
                    continue
                elif y < end_y:
                    break
                first_index = index
                while (index < len(self.hot_pixels)
                       and self.hot_pixels[index].y == y):
                    index += 1
                last_index = index
                self.hot_pixel_set_left_to_right(
                        y, start_x, end_x, bound, first_index, last_index,
                        y != end_point.y or add_end_point)
        bound.last_point = end_point

    def insert_lm_left_and_right_bound(self,
                                       operation_kind: OperationKind,
                                       subject_fill_kind: FillKind,
                                       clip_fill_kind: FillKind,
                                       scanbeams: List[Coordinate],
                                       left_bound: Bound,
                                       right_bound: Bound,
                                       active_bounds: List[Bound]) -> None:
        bound_index = insert_bound_into_abl(left_bound, right_bound,
                                            active_bounds)
        set_winding_count(bound_index, active_bounds, subject_fill_kind,
                          clip_fill_kind)
        bound = active_bounds[bound_index]
        next_bound = active_bounds[bound_index + 1]
        next_bound.winding_count = bound.winding_count
        next_bound.opposite_winding_count = bound.opposite_winding_count
        if left_bound.is_contributing(operation_kind, subject_fill_kind,
                                      clip_fill_kind):
            self.add_local_minimum_point(bound.current_edge.bottom, bound,
                                         next_bound, active_bounds)
        # add edges' top to scanbeams
        insort_unique(scanbeams, bound.current_edge.top.y)
        if not next_bound.current_edge.is_horizontal:
            insort_unique(scanbeams, next_bound.current_edge.top.y)

    def insert_local_minima_into_abl(self,
                                     operation_kind: OperationKind,
                                     subject_fill_kind: FillKind,
                                     clip_fill_kind: FillKind,
                                     bot_y: Coordinate,
                                     scanbeams: List[Coordinate],
                                     minimums: LocalMinimumList,
                                     minimums_index: int,
                                     active_bounds: List[Bound]) -> int:
        while (minimums_index < len(minimums)
               and minimums[minimums_index].y == bot_y):
            minimum = minimums[minimums_index]
            minimum.initialize()
            self.insert_lm_left_and_right_bound(
                    operation_kind, subject_fill_kind, clip_fill_kind,
                    scanbeams, minimum.left_bound, minimum.right_bound,
                    active_bounds)
            minimums_index += 1
        return minimums_index

    def insert_local_minima_into_abl_hot_pixel(self,
                                               top_y: Coordinate,
                                               minimums: List[LocalMinimum],
                                               minimums_index: int,
                                               active_bounds: List[Bound],
                                               scanbeams: List[Coordinate]
                                               ) -> int:
        while (minimums_index < len(minimums)
               and minimums[minimums_index].y == top_y):
            current_lm = minimums[minimums_index]
            self.hot_pixels.append(current_lm.left_bound.edges[0].bottom)
            left_bound, right_bound = (current_lm.left_bound,
                                       current_lm.right_bound)

            left_bound.current_edge_index = 0
            left_bound.next_edge_index = 1
            left_bound.current_x = left_bound.current_edge.bottom.x

            right_bound.current_edge_index = 0
            right_bound.next_edge_index = 1
            right_bound.current_x = right_bound.current_edge.bottom.x

            lb_abl_index = insert_bound_into_abl(left_bound, right_bound,
                                                 active_bounds)
            lb_abl_current_edge = active_bounds[lb_abl_index].current_edge
            if not lb_abl_current_edge.is_horizontal:
                insort_unique(scanbeams, lb_abl_current_edge.top.y)
            rb_abl_index = lb_abl_index + 1
            rb_abl_current_edge = active_bounds[rb_abl_index].current_edge
            if not rb_abl_current_edge.is_horizontal:
                insort_unique(scanbeams, rb_abl_current_edge.top.y)
            minimums_index += 1
        return minimums_index

    def intersect_bounds(self,
                         point: Point,
                         operation_kind: OperationKind,
                         subject_fill_kind: FillKind,
                         clip_fill_kind: FillKind,
                         first_bound: Bound,
                         second_bound: Bound,
                         active_bounds: List[Bound]) -> None:
        first_bound_contributing = first_bound.ring is not None
        second_bound_contributing = second_bound.ring is not None
        # update winding counts,
        # assumes that first bound will be to the right of second bound
        # above the intersection
        if first_bound.polygon_kind is second_bound.polygon_kind:
            if first_bound.is_even_odd_fill_kind(subject_fill_kind,
                                                 clip_fill_kind):
                first_bound.winding_count, second_bound.winding_count = (
                    second_bound.winding_count, first_bound.winding_count)
            else:
                if first_bound.winding_count + second_bound.winding_delta == 0:
                    first_bound.winding_count = -first_bound.winding_count
                else:
                    first_bound.winding_count += second_bound.winding_delta
                if second_bound.winding_count - first_bound.winding_delta == 0:
                    second_bound.winding_count = -second_bound.winding_count
                else:
                    second_bound.winding_count -= first_bound.winding_delta
        else:
            if not second_bound.is_even_odd_fill_kind(subject_fill_kind,
                                                      clip_fill_kind):
                first_bound.opposite_winding_count += (
                    second_bound.winding_delta)
            else:
                first_bound.opposite_winding_count = int(
                        first_bound.opposite_winding_count == 0)
            if not first_bound.is_even_odd_fill_kind(subject_fill_kind,
                                                     clip_fill_kind):
                second_bound.opposite_winding_count -= (
                    first_bound.winding_delta)
            else:
                second_bound.opposite_winding_count = int(
                        second_bound.opposite_winding_count == 0)
        if first_bound.polygon_kind is PolygonKind.SUBJECT:
            first_bound_fill_kind, first_bound_complement_fill_kind = (
                subject_fill_kind, clip_fill_kind)
        else:
            first_bound_fill_kind, first_bound_complement_fill_kind = (
                clip_fill_kind, subject_fill_kind)
        if second_bound.polygon_kind is PolygonKind.SUBJECT:
            second_bound_fill_kind, second_bound_composite_fill_kind = (
                subject_fill_kind, clip_fill_kind)
        else:
            second_bound_fill_kind, second_bound_composite_fill_kind = (
                clip_fill_kind, subject_fill_kind)
        if first_bound_fill_kind is FillKind.POSITIVE:
            first_bound_winding_count = first_bound.winding_count
        elif first_bound_fill_kind is FillKind.NEGATIVE:
            first_bound_winding_count = -first_bound.winding_count
        else:
            first_bound_winding_count = abs(first_bound.winding_count)
        if second_bound_fill_kind is FillKind.POSITIVE:
            second_bound_winding_count = second_bound.winding_count
        elif second_bound_fill_kind is FillKind.NEGATIVE:
            second_bound_winding_count = -second_bound.winding_count
        else:
            second_bound_winding_count = abs(second_bound.winding_count)
        if first_bound_contributing and second_bound_contributing:
            if (first_bound_winding_count != 0
                    and first_bound_winding_count != 1
                    or second_bound_winding_count != 0
                    and second_bound_winding_count != 1
                    or (first_bound.polygon_kind
                        is not second_bound.polygon_kind)
                    and operation_kind is not OperationKind.XOR):
                self.add_local_maximum_point(point, first_bound, second_bound,
                                             active_bounds)
            else:
                self.add_point(first_bound, active_bounds, point)
                self.add_point(second_bound, active_bounds, point)
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif first_bound_contributing:
            if (second_bound_winding_count == 0
                    or second_bound_winding_count == 1):
                self.add_point(first_bound, active_bounds, point)
                second_bound.last_point = point
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif second_bound_contributing:
            if (first_bound_winding_count == 0
                    or first_bound_winding_count == 1):
                first_bound.last_point = point
                self.add_point(second_bound, active_bounds, point)
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif ((first_bound_winding_count == 0
               or first_bound_winding_count == 1)
              and (second_bound_winding_count == 0
                   or second_bound_winding_count == 1)):
            # neither bound is currently contributing
            if first_bound_complement_fill_kind is FillKind.POSITIVE:
                first_bound_opposite_winding_count = (
                    first_bound.opposite_winding_count)
            elif first_bound_complement_fill_kind is FillKind.NEGATIVE:
                first_bound_opposite_winding_count = (
                    -first_bound.opposite_winding_count)
            else:
                first_bound_opposite_winding_count = abs(
                        first_bound.opposite_winding_count)
            if second_bound_composite_fill_kind is FillKind.POSITIVE:
                second_bound_opposite_winding_count = (
                    second_bound.opposite_winding_count)
            elif second_bound_composite_fill_kind is FillKind.NEGATIVE:
                second_bound_opposite_winding_count = (
                    -second_bound.opposite_winding_count)
            else:
                second_bound_opposite_winding_count = abs(
                        second_bound.opposite_winding_count)
            if first_bound.polygon_kind is not second_bound.polygon_kind:
                self.add_local_minimum_point(point, first_bound, second_bound,
                                             active_bounds)
            elif (first_bound_winding_count == 1
                  and second_bound_winding_count == 1):
                if operation_kind is OperationKind.INTERSECTION:
                    if (first_bound_opposite_winding_count > 0
                            and second_bound_opposite_winding_count > 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                elif operation_kind is OperationKind.UNION:
                    if (first_bound_opposite_winding_count <= 0
                            and second_bound_opposite_winding_count <= 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                elif operation_kind is OperationKind.DIFFERENCE:
                    if (first_bound.polygon_kind is PolygonKind.CLIP
                            and first_bound_opposite_winding_count > 0
                            and second_bound_opposite_winding_count > 0
                            or first_bound.polygon_kind is PolygonKind.SUBJECT
                            and first_bound_opposite_winding_count <= 0
                            and second_bound_opposite_winding_count <= 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                else:
                    self.add_local_minimum_point(point, first_bound,
                                                 second_bound,
                                                 active_bounds)
            else:
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)

    def process_edges_at_top_of_scanbeam(self,
                                         operation_kind: OperationKind,
                                         subject_fill_kind: FillKind,
                                         clip_fill_kind: FillKind,
                                         top_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         active_bounds: List[Bound],
                                         minimums_index: int,
                                         minimums: LocalMinimumList
                                         ) -> Tuple[List[Bound], int]:
        bound_index = 0
        while bound_index < len(active_bounds):
            bound = active_bounds[bound_index]
            if bound is None:
                bound_index += 1
                continue
            # 1) process maxima,
            # treating them as if they are "bent" horizontal edges,
            # but exclude maxima with horizontal edges
            is_maxima_edge = bound.is_maxima(top_y)
            if is_maxima_edge:
                bound_maximum_index = find(bound.maximum_bound, active_bounds)
                is_maxima_edge = (bound_maximum_index == len(active_bounds)
                                  or not (active_bounds[bound_maximum_index]
                                          .current_edge.is_horizontal)
                                  and (active_bounds[bound_maximum_index]
                                       .is_maxima(top_y)))
                if is_maxima_edge:
                    bound_index = self.do_maxima(
                            operation_kind, subject_fill_kind, clip_fill_kind,
                            bound_index, bound_maximum_index, active_bounds)
                    continue
            # 2) promote horizontal edges
            bound = active_bounds[bound_index]
            if bound.is_intermediate(top_y) and bound.next_edge.is_horizontal:
                if bound.ring is not None:
                    self.insert_hot_pixels_in_path(
                            bound, bound.current_edge.top, False)
                bound.to_next_edge(scanbeams)
                if bound.ring is not None:
                    self.add_point_to_ring(bound, bound.current_edge.bottom)
            else:
                bound.current_x = bound.current_edge.get_current_x(top_y)
            bound_index += 1
        active_bounds = list(filter(partial(is_not, None), active_bounds))
        minimums_index = self.insert_horizontal_local_minima_into_abl(
                operation_kind, subject_fill_kind, clip_fill_kind, top_y,
                scanbeams, minimums, minimums_index, active_bounds)
        active_bounds = self.process_horizontals(
                operation_kind, subject_fill_kind, clip_fill_kind,
                top_y, scanbeams, active_bounds)
        # 4) promote intermediate vertices
        for bound in active_bounds:
            if bound.is_intermediate(top_y):
                if bound.ring is not None:
                    self.add_point_to_ring(bound, bound.current_edge.top)
                bound.to_next_edge(scanbeams)
        return active_bounds, minimums_index

    def process_horizontal(self,
                           operation_kind: OperationKind,
                           subject_fill_kind: FillKind,
                           clip_fill_kind: FillKind,
                           scanline_y: Coordinate,
                           scanbeams: List[Coordinate],
                           bound_index: int,
                           active_bounds: List[Optional[Bound]]) -> int:
        bound = active_bounds[bound_index]
        return (self.process_horizontal_left_to_right
                if bound.current_edge.bottom.x < bound.current_edge.top.x
                else self.process_horizontal_right_to_left)(
                operation_kind, subject_fill_kind, clip_fill_kind, scanline_y,
                scanbeams, bound_index, active_bounds)

    def process_horizontals(self,
                            operation_kind: OperationKind,
                            subject_fill_kind: FillKind,
                            clip_fill_kind: FillKind,
                            scanline_y: Coordinate,
                            scanbeams: List[Coordinate],
                            active_bounds: List[Bound]) -> List[Bound]:
        active_bounds = list(active_bounds)
        index = 0
        while index < len(active_bounds):
            bound = active_bounds[index]
            if bound is not None and bound.current_edge.is_horizontal:
                index = self.process_horizontal(
                        operation_kind, subject_fill_kind, clip_fill_kind,
                        scanline_y, scanbeams, index, active_bounds)
            else:
                index += 1
        return list(filter(partial(is_not, None), active_bounds))

    def process_horizontal_left_to_right(self,
                                         operation_kind: OperationKind,
                                         subject_fill_kind: FillKind,
                                         clip_fill_kind: FillKind,
                                         scanline_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         bound_index: int,
                                         active_bounds: List[Optional[Bound]]
                                         ) -> int:
        shifted = False
        result = bound_index
        bound = active_bounds[bound_index]
        is_maxima_edge = bound.is_maxima(scanline_y)
        maximum_bound_index = len(active_bounds)
        if is_maxima_edge:
            maximum_bound_index = find(bound.maximum_bound, active_bounds)
        hot_pixel_index = self.current_hot_pixel_index
        while (hot_pixel_index < len(self.hot_pixels)
               and (self.hot_pixels[hot_pixel_index].y > scanline_y
                    or self.hot_pixels[hot_pixel_index].y == scanline_y
                    and (self.hot_pixels[hot_pixel_index].x
                         < bound.current_edge.bottom.x))):
            hot_pixel_index += 1
        next_bound_index = bound_index + 1
        while next_bound_index < len(active_bounds):
            next_bound = active_bounds[next_bound_index]
            if next_bound is None:
                next_bound_index += 1
                continue
            # insert extra coordinates into horizontal edges
            # (in output polygons)
            # wherever hot pixels touch these horizontal edges,
            # this helps 'simplifying' polygons
            # (i.e. if the simplify property is set)
            while (hot_pixel_index < len(self.hot_pixels)
                   and self.hot_pixels[hot_pixel_index].y == scanline_y
                   and (self.hot_pixels[hot_pixel_index].x
                        < round_half_up(next_bound.current_x))
                   and (self.hot_pixels[hot_pixel_index].x
                        < bound.current_edge.top.x)):
                if bound.ring is not None:
                    self.add_point_to_ring(bound,
                                           self.hot_pixels[hot_pixel_index])
                hot_pixel_index += 1
            if are_floats_greater_than(next_bound.current_x,
                                       float(bound.current_edge.top.x)):
                break
            # break if we've got to the end of an intermediate horizontal edge,
            # smaller dx's are to the right of larger dx's above the horizontal
            if (round_half_up(next_bound.current_x) == bound.current_edge.top.x
                    and bound.next_edge_index < len(bound.edges)
                    and bound.current_edge.slope < bound.next_edge.slope):
                break
            # may be done multiple times
            if bound.ring is not None:
                self.add_point_to_ring(
                        bound,
                        Point(round_half_up(next_bound.current_x), scanline_y))
            # so far we're still in range of the horizontal edge
            # but make sure we're at the last of consecutive horizontals
            # when matching with maximum bound
            if is_maxima_edge and next_bound_index == maximum_bound_index:
                if bound.ring is not None and next_bound.ring is not None:
                    self.add_local_maximum_point(bound.current_edge.top, bound,
                                                 next_bound, active_bounds)
                active_bounds[maximum_bound_index] = None
                active_bounds[bound_index] = None
                return result + (not shifted)
            self.intersect_bounds(Point(round_half_up(next_bound.current_x),
                                        scanline_y), operation_kind,
                                  subject_fill_kind, clip_fill_kind, bound,
                                  next_bound, active_bounds)
            active_bounds[bound_index], active_bounds[next_bound_index] = (
                active_bounds[next_bound_index], active_bounds[bound_index])
            bound_index = next_bound_index
            bound = active_bounds[bound_index]
            next_bound_index += 1
            shifted = True
        if bound.ring is not None:
            while (hot_pixel_index < len(self.hot_pixels)
                   and self.hot_pixels[hot_pixel_index].y == scanline_y
                   and (self.hot_pixels[hot_pixel_index].x
                        < bound.current_edge.top.x)):
                self.add_point_to_ring(bound, self.hot_pixels[hot_pixel_index])
                hot_pixel_index += 1
        if bound.ring is not None:
            self.add_point_to_ring(bound, bound.current_edge.top)
        if bound.next_edge_index < len(bound.edges):
            bound.to_next_edge(scanbeams)
        else:
            active_bounds[bound_index] = None
        return result + (not shifted)

    def process_horizontal_right_to_left(self,
                                         operation_kind: OperationKind,
                                         subject_fill_kind: FillKind,
                                         clip_fill_kind: FillKind,
                                         scanline_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         bound_index: int,
                                         active_bounds: List[Optional[Bound]]
                                         ) -> int:
        bound = active_bounds[bound_index]
        result = bound_index + 1
        is_maxima_edge = bound.is_maxima(scanline_y)
        maximum_bound_index = len(active_bounds)
        if is_maxima_edge:
            maximum_bound_index = find(bound.maximum_bound, active_bounds)
        hot_pixel_index = self.current_hot_pixel_index
        while (hot_pixel_index < len(self.hot_pixels)
               and (self.hot_pixels[hot_pixel_index].y < scanline_y
                    or self.hot_pixels[hot_pixel_index].y == scanline_y
                    and (self.hot_pixels[hot_pixel_index].x
                         < bound.current_edge.top.x))):
            hot_pixel_index += 1
        hot_pixel_index -= 1
        prev_bound_index = bound_index - 1
        bound_index = prev_bound_index + 1
        bound = active_bounds[bound_index]
        while prev_bound_index >= 0:
            prev_bound = active_bounds[prev_bound_index]
            if prev_bound is None:
                prev_bound_index -= 1
                continue
            while (hot_pixel_index >= 0
                   and self.hot_pixels[hot_pixel_index].y == scanline_y
                   and (self.hot_pixels[hot_pixel_index].x
                        > round_half_up(prev_bound.current_x))
                   and (self.hot_pixels[hot_pixel_index].x
                        > bound.current_edge.top.x)):
                if bound.ring is not None:
                    self.add_point_to_ring(bound,
                                           self.hot_pixels[hot_pixel_index])
                hot_pixel_index -= 1
            if are_floats_less_than(prev_bound.current_x,
                                    float(bound.current_edge.top.x)):
                break
            # break if we've got to the end of an intermediate horizontal edge,
            # smaller dx's are to the right of larger dx's above the horizontal
            if (round_half_up(prev_bound.current_x) == bound.current_edge.top.x
                    and bound.next_edge_index < len(bound.edges)
                    and bound.current_edge.slope < bound.next_edge.slope):
                break
            # may be done multiple times
            if bound.ring is not None:
                self.add_point_to_ring(
                        bound,
                        Point(round_half_up(prev_bound.current_x), scanline_y))
            # so far we're still in range of the horizontal edge
            # but make sure we're at the last of consecutive horizontals
            # when matching with maximum bound
            if is_maxima_edge and prev_bound_index == maximum_bound_index:
                if bound.ring is not None and prev_bound.ring is not None:
                    self.add_local_maximum_point(bound.current_edge.top, bound,
                                                 prev_bound, active_bounds)
                active_bounds[prev_bound_index] = None
                active_bounds[bound_index] = None
                return result
            self.intersect_bounds(Point(round_half_up(prev_bound.current_x),
                                        scanline_y), operation_kind,
                                  subject_fill_kind, clip_fill_kind,
                                  prev_bound, bound, active_bounds)
            active_bounds[prev_bound_index], active_bounds[bound_index] = (
                active_bounds[bound_index], active_bounds[prev_bound_index])
            bound_index = prev_bound_index
            prev_bound_index -= 1
        if bound.ring is not None:
            while (hot_pixel_index >= 0
                   and self.hot_pixels[hot_pixel_index].y == scanline_y
                   and (self.hot_pixels[hot_pixel_index].x
                        > bound.current_edge.top.x)):
                self.add_point_to_ring(bound, self.hot_pixels[hot_pixel_index])
                hot_pixel_index -= 1
        if bound.ring is not None:
            self.add_point_to_ring(bound, bound.current_edge.top)
        if bound.next_edge_index < len(bound.edges):
            bound.to_next_edge(scanbeams)
        else:
            active_bounds[bound_index] = None
        return result

    def process_hot_pixel_edges_at_top_of_scanbeam(self,
                                                   top_y: Coordinate,
                                                   scanbeams: List[Coordinate],
                                                   active_bounds: List[Bound]
                                                   ) -> List[Bound]:
        active_bounds = list(active_bounds)
        index = 0
        while index < len(active_bounds):
            bound = active_bounds[index]
            if bound is None:
                index += 1
                continue
            shifted = False
            current_index = index
            while (bound.current_edge_index < len(bound.edges)
                   and bound.current_edge.top.y == top_y):
                current_edge = bound.current_edge
                self.hot_pixels.append(current_edge.top)
                if current_edge.is_horizontal:
                    current_index, shifted = self.horizontals_at_top_scanbeam(
                            top_y, active_bounds, current_index)
                bound.to_next_edge(scanbeams)
            if bound.current_edge_index == len(bound.edges):
                active_bounds[current_index] = None
            if not shifted:
                index += 1
        return list(filter(partial(is_not, None), active_bounds))

    def process_hot_pixel_intersections(self,
                                        top_y: Coordinate,
                                        active_bounds: List[Bound]
                                        ) -> List[Bound]:
        update_current_x(active_bounds, top_y)
        return bubble_sort(active_bounds, intersection_compare,
                           self.hot_pixels_on_swap)

    def process_intersections(self,
                              top_y: Coordinate,
                              operation_kind: OperationKind,
                              subject_fill_kind: FillKind,
                              clip_fill_kind: FillKind,
                              active_bounds: List[Bound]) -> None:
        if not active_bounds:
            return
        update_current_x(active_bounds, top_y)
        _, intersections = build_intersect_list(active_bounds)
        if not intersections:
            return
        self.process_intersect_list(sorted(intersections), operation_kind,
                                    subject_fill_kind, clip_fill_kind,
                                    active_bounds)

    def process_intersect_list(self, intersections: List[IntersectNode],
                               operation_kind: OperationKind,
                               subject_fill_kind: FillKind,
                               clip_fill_kind: FillKind,
                               active_bounds: List[Bound]) -> None:
        for index in range(len(intersections)):
            first_index = find_if(intersections[index].has_bound,
                                  active_bounds)
            second_index = first_index + 1
            if not intersections[index].has_bound(active_bounds[second_index]):
                for next_index in range(index + 1, len(intersections)):
                    next_node = intersections[next_index]
                    candidate_first_index = find_if(next_node.has_bound,
                                                    active_bounds)
                    candidate_second_index = candidate_first_index + 1
                    if next_node.has_bound(
                            active_bounds[candidate_second_index]):
                        first_index = candidate_first_index
                        second_index = candidate_second_index
                        break
                else:
                    raise RuntimeError('Could not properly correct '
                                       'intersection order.')
                intersections[index], intersections[next_index] = (
                    intersections[next_index], intersections[index])
            self.intersect_bounds(intersections[index].point.round(),
                                  operation_kind, subject_fill_kind,
                                  clip_fill_kind,
                                  intersections[index].first_bound,
                                  intersections[index].second_bound,
                                  active_bounds)
            active_bounds[first_index], active_bounds[second_index] = (
                active_bounds[second_index], active_bounds[first_index])

    def remove_duplicate_points(self,
                                first_node: PointNode,
                                second_node: PointNode) -> bool:
        if first_node.ring is second_node.ring:
            if first_node.next is second_node:
                first_node.next = second_node.next
                first_node.next.prev = first_node
                second_node.prev = second_node.next = second_node.ring = None
                if first_node.ring.node is second_node:
                    first_node.ring.node = first_node
                return True
            elif second_node.next is first_node:
                first_node.prev = second_node.prev
                first_node.prev.next = first_node
                second_node.prev = second_node.next = second_node.ring = None
                if first_node.ring.node is second_node:
                    first_node.ring.node = first_node
                return True
        while (first_node.next == first_node
               and first_node.next is not first_node):
            outsider = first_node.prev
            first_node.prev = outsider.prev
            first_node.prev.next = first_node
            outsider.prev = outsider.next = outsider.ring = None
            if first_node.ring.node is outsider:
                first_node.ring.node = first_node
        if first_node.next is first_node:
            self.remove_ring_and_points(first_node.ring, False)
            return True
        if second_node.ring is None:
            return True
        while (second_node.next == second_node
               and second_node.next is not second_node):
            outsider = second_node.next
            second_node.next = outsider.next
            second_node.next.prev = second_node
            outsider.prev = outsider.next = outsider.ring = None
            if second_node.ring.node is outsider:
                second_node.ring.node = second_node
        while (second_node.prev == second_node
               and second_node.prev is not second_node):
            outsider = second_node.prev
            second_node.prev = outsider.prev
            second_node.prev.next = second_node
            outsider.prev = outsider.next = outsider.ring = None
            if second_node.ring.node is outsider:
                second_node.ring.node = second_node
        if second_node.next is second_node:
            self.remove_ring_and_points(second_node.ring, False)
            return True
        return first_node.ring is None

    def remove_ring_and_points(self,
                               ring: Ring,
                               remove_children: bool = True,
                               remove_from_parent: bool = True) -> None:
        for index, child in enumerate(ring.children):
            if child is None:
                continue
            if remove_children:
                self.remove_ring_and_points(child, True, False)
            ring.children[index] = None
        if remove_from_parent:
            # remove the old child relationship
            remove_from_children(ring,
                                 self.children
                                 if ring.parent is None
                                 else ring.parent.children)
        node = ring.node
        if node is not None:
            node.prev.next = None
            while node is not None:
                node.prev, node.next, node.ring, node = (None, None, None,
                                                         node.next)
        ring.node = None
        ring.reset_stats()

    def replace_ring(self,
                     original: Optional[Ring],
                     replacement: Ring) -> None:
        assert original is not replacement
        original_children = (self.children
                             if original is None
                             else original.children)
        for index, child in enumerate(replacement.children):
            if child is None:
                continue
            child.parent = original
            set_to_children(child, original_children)
            replacement.children[index] = None
        # remove the old child relationship
        remove_from_children(replacement,
                             self.children
                             if replacement.parent is None
                             else replacement.parent.children)
        replacement.node = None
        replacement.reset_stats()

    def set_hole_state(self, bound: Bound, active_bounds: List[Bound]) -> None:
        bound_index = next(index
                           for index in range(len(active_bounds) - 1, -1, -1)
                           if active_bounds[index] is bound)
        bound_index -= 1
        bound_temp = None
        while bound_index >= 0:
            current_bound = active_bounds[bound_index]
            if current_bound is not None and current_bound.ring is not None:
                if bound_temp is None:
                    bound_temp = current_bound
                elif bound_temp.ring is current_bound.ring:
                    bound_temp = None
            bound_index -= 1
        if bound_temp is None:
            bound.ring.parent = None
            self.children.append(bound.ring)
        else:
            bound.ring.parent = bound_temp.ring
            bound_temp.ring.children.append(bound.ring)

    def sort_hot_pixels(self) -> None:
        quicksort(self.hot_pixels,
                  hot_pixels_compare)
        self.hot_pixels = [key for key, _ in groupby(self.hot_pixels)]

    def update_current_hot_pixel_index(self, scanline_y: Coordinate) -> None:
        while self.hot_pixels[self.current_hot_pixel_index].y > scanline_y:
            self.current_hot_pixel_index += 1


def update_current_x(active_bounds: List[Bound], top_y: Coordinate) -> None:
    for position, bound in enumerate(active_bounds):
        bound.position = position
        bound.current_x = bound.current_edge.get_current_x(top_y)


def hot_pixels_compare(left: Point, right: Point) -> bool:
    return not (left.x < right.x
                if left.y == right.y
                else left.y > right.y)
