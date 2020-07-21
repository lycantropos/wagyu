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
                    intersection_compare)
from .bubble_sort import bubble_sort
from .enums import EdgeSide
from .hints import Coordinate
from .local_minimum import (LocalMinimum,
                            LocalMinimumList)
from .point import Point
from .point_node import (PointNode,
                         maybe_point_node_to_points)
from .ring import Ring
from .utils import (insort_unique,
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
        return [list(node) for node in self.nodes]

    @property
    def stored_points(self) -> List[List[Point]]:
        return [list(node) for node in self.storage]

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

    def process_hot_pixel_edges_at_top_of_scanbeam(self,
                                                   top_y: Coordinate,
                                                   scanbeams: List[Coordinate],
                                                   active_bounds: List[Bound]
                                                   ) -> List[Bound]:
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

    def sort_hot_pixels(self) -> None:
        quicksort(self.hot_pixels,
                  hot_pixels_compare)
        self.hot_pixels = [key for key, _ in groupby(self.hot_pixels)]

    def process_hot_pixel_intersections(self,
                                        top_y: Coordinate,
                                        active_bounds: List[Bound]
                                        ) -> List[Bound]:
        update_current_x(active_bounds, top_y)
        return bubble_sort(active_bounds, intersection_compare,
                           self.hot_pixels_on_swap)

    def hot_pixels_on_swap(self,
                           first_bound: Bound,
                           second_bound: Bound) -> None:
        intersection = first_bound.current_edge & second_bound.current_edge
        if intersection is None:
            raise RuntimeError('Trying to find intersection of lines '
                               'that do not intersect')
        self.hot_pixels.append(intersection.round())

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
            new_node = self.create_point_node(hot_pixel, op, bound.ring)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_start - 1
        return hot_pixel_index

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
            new_node = self.create_point_node(hot_pixel, op, bound.ring)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_stop
        return hot_pixel_index

    def create_point_node(self, point: Point, before_this_point: PointNode,
                          ring: Optional[Ring]) -> PointNode:
        result = PointNode(point.x, point.y)
        result.ring = ring
        result.place_before(before_this_point)
        self.nodes.append(result)
        self.all_nodes.append(result)
        return result

    def create_ring(self) -> Ring:
        result = Ring(self.index)
        self.index += 1
        self.rings.append(result)
        return result


def update_current_x(active_bounds: List[Bound], top_y: Coordinate) -> None:
    for position, bound in enumerate(active_bounds):
        bound.position = position
        bound.current_x = bound.current_edge.get_current_x(top_y)


def hot_pixels_compare(left: Point, right: Point) -> bool:
    return not (left.x < right.x
                if left.y == right.y
                else left.y > right.y)


def quicksort(array, compare_func):
    _quicksort(array, 0, len(array) - 1, compare_func)


def _quicksort(array, start, end, compare_func):
    if start >= end:
        return

    p = partition(array, start, end, compare_func)
    _quicksort(array, start, p - 1, compare_func)
    _quicksort(array, p + 1, end, compare_func)


def partition(array, start, end, compare_func):
    pivot = array[start]
    low = start + 1
    high = end
    while True:
        while low <= high and compare_func(array[high], pivot):
            high = high - 1
        while low <= high and not compare_func(array[low], pivot):
            low = low + 1
        if low <= high:
            array[low], array[high] = array[high], array[low]
        else:
            break
    array[start], array[high] = array[high], array[start]
    return high
