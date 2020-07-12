import math
from functools import partial
from itertools import groupby
from operator import is_not
from typing import (List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from .bound import Bound
from .bubble_sort import bubble_sort
from .hints import Coordinate
from .local_minimum import (LocalMinimum,
                            LocalMinimumList)
from .point import Point
from .point_node import (PointNode,
                         maybe_point_node_to_points)
from .ring import Ring
from .utils import (are_edges_slopes_equal,
                    are_floats_almost_equal,
                    are_floats_greater_than,
                    are_floats_less_than,
                    insort_unique)


class RingManager:
    __slots__ = ('children', 'all_nodes', 'hot_pixels', 'nodes', 'rings',
                 'storage', 'index')

    def __init__(self,
                 children: Optional[List[Optional[Ring]]] = None,
                 hot_pixels: Optional[List[Point]] = None,
                 rings: Optional[List[Ring]] = None,
                 index: int = 0) -> None:
        self.children = [] if children is None else children
        self.hot_pixels = [] if hot_pixels is None else hot_pixels
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
    def points(self) -> List[List[Point]]:
        return [list(node) for node in self.nodes]

    @property
    def stored_points(self) -> List[List[Point]]:
        return [list(node) for node in self.storage]

    def build_hot_pixels(self, minimums: LocalMinimumList) -> None:
        sorted_minimums = sorted(minimums,
                                 reverse=True)
        current_lm_index = 0
        scanbeams = minimums.scanbeams
        active_bounds = []  # type: List[Optional[Bound]]
        scanline_y = math.inf
        while scanbeams or current_lm_index < len(minimums):
            try:
                scanline_y = scanbeams.pop()
            except IndexError:
                pass
            self.process_hot_pixel_intersections(scanline_y, active_bounds)
            current_lm_index = self.insert_local_minima_into_abl_hot_pixel(
                    scanline_y, current_lm_index, scanbeams, sorted_minimums,
                    active_bounds)
            self.process_hot_pixel_edges_at_top_of_scanbeam(scanline_y,
                                                            scanbeams,
                                                            active_bounds)
        self.sort_hot_pixels()

    def insert_local_minima_into_abl_hot_pixel(self,
                                               top_y: Coordinate,
                                               current_lm_index: int,
                                               scanbeams: List[Coordinate],
                                               minimums: List[LocalMinimum],
                                               active_bounds: List[Bound]
                                               ) -> int:
        while (current_lm_index < len(minimums)
               and minimums[current_lm_index].y == top_y):
            current_lm = minimums[current_lm_index]
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
            current_lm_index += 1
        return current_lm_index

    def process_hot_pixel_edges_at_top_of_scanbeam(self,
                                                   top_y: Coordinate,
                                                   scanbeams: List[Coordinate],
                                                   active_bounds: List[Bound]
                                                   ) -> None:
        index = 0
        while index < len(active_bounds):
            bound = active_bounds[index]
            if bound is None:
                index += 1
                continue
            shifted = False
            while (bound.current_edge_index < len(bound.edges)
                   and bound.current_edge.top.y == top_y):
                current_edge = bound.current_edge
                self.hot_pixels.append(current_edge.top)
                if current_edge.is_horizontal:
                    index, shifted = horizontals_at_top_scanbeam(top_y, index,
                                                                 active_bounds,
                                                                 self)
                next_edge_in_bound(bound, scanbeams)
            if bound.current_edge_index == len(bound.edges):
                active_bounds[index] = None
            if not shifted:
                index += 1
        active_bounds[:] = filter(partial(is_not, None), active_bounds)

    def sort_hot_pixels(self) -> None:
        quicksort(self.hot_pixels,
                  hot_pixels_compare)
        self.hot_pixels = [key for key, _ in groupby(self.hot_pixels)]

    def process_hot_pixel_intersections(self,
                                        top_y: Coordinate,
                                        active_bounds: List[Bound]) -> None:
        if not active_bounds:
            return
        update_current_x(active_bounds, top_y)
        bubble_sort(active_bounds, intersection_compare,
                    self.hot_pixels_on_swap)

    def hot_pixels_on_swap(self,
                           first_bound: Bound,
                           second_bound: Bound) -> None:
        intersection = first_bound.current_edge & second_bound.current_edge
        if intersection is None:
            raise RuntimeError('Trying to find intersection of lines '
                               'that do not intersect')
        self.hot_pixels.append(intersection.round())


def update_current_x(active_bounds: List[Bound], top_y: Coordinate) -> None:
    for position, bound in enumerate(active_bounds):
        bound.position = position
        bound.current_x = bound.current_edge.get_current_x(top_y)


def intersection_compare(left: Bound, right: Bound) -> bool:
    return not (left.current_x > right.current_x and
                not are_edges_slopes_equal(left.current_edge,
                                           right.current_edge))


def bound_insert_location(left: Bound, right: Bound) -> bool:
    if are_floats_almost_equal(left.current_x, right.current_x):
        if left.current_edge.top.y > right.current_edge.top.y:
            return are_floats_less_than(left.current_edge.top.x,
                                        right.current_edge.get_current_x(
                                                left.current_edge.top.y))
        else:
            return are_floats_greater_than(right.current_edge.top.x,
                                           left.current_edge.get_current_x(
                                                   right.current_edge.top.y))
    else:
        return left.current_x < right.current_x


def insert_bound_into_abl(left: Bound,
                          right: Bound,
                          active_bounds: List[Bound]) -> int:
    index = 0
    for index, bound in enumerate(active_bounds):
        if bound_insert_location(left, bound):
            break
    active_bounds.insert(index, right)
    active_bounds.insert(index, left)
    return index


def horizontals_at_top_scanbeam(top_y: Coordinate,
                                bound_index: int,
                                active_bounds: List[Bound],
                                manager: RingManager) -> Tuple[int, bool]:
    shifted = False
    current_edge = active_bounds[bound_index].current_edge
    active_bounds[bound_index].current_x = current_edge.top.x
    if current_edge.bottom.x < current_edge.top.x:
        bound_next_index = bound_index + 1
        while (bound_next_index < len(active_bounds)
               and (active_bounds[bound_next_index] is None
                    or active_bounds[bound_next_index].current_x
                    < active_bounds[bound_index].current_x)):
            bound_next = active_bounds[bound_next_index]
            if (bound_next is not None
                    and bound_next.current_edge.top.y != top_y
                    and bound_next.current_edge.bottom.y != top_y):
                pt = Point(round(bound_next.current_x), top_y)
                manager.hot_pixels.append(pt)
            active_bounds[bound_index], active_bounds[bound_next_index] = (
                active_bounds[bound_next_index], active_bounds[bound_index])
            bound_index += 1
            bound_next_index += 1
            shifted = True
    elif bound_index > 0:
        bound_prev_index = bound_index - 1
        while (bound_index > 0
               and (active_bounds[bound_prev_index] is None
                    or active_bounds[bound_prev_index].current_x
                    > active_bounds[bound_index].current_x)):
            bound_prev = active_bounds[bound_prev_index]
            if (bound_prev is not None
                    and bound_prev.current_edge.top.y != top_y
                    and bound_prev.current_edge.bottom.y != top_y):
                pt = Point(round(bound_prev.current_x), top_y)
                manager.hot_pixels.append(pt)
            active_bounds[bound_index], active_bounds[bound_prev_index] = (
                active_bounds[bound_prev_index],
                active_bounds[bound_index])
            bound_index -= 1
            if bound_index > 0:
                bound_prev_index -= 1
    return bound_index, shifted


def next_edge_in_bound(bound: Bound, scanbeams: List[Coordinate]) -> None:
    bound.current_edge_index += 1
    current_edge_index = bound.current_edge_index
    if current_edge_index < len(bound.edges):
        bound.next_edge_index += 1
        bound.current_x = bound.current_edge.bottom.x
        if not bound.current_edge.is_horizontal:
            insort_unique(scanbeams, bound.current_edge.top.y)


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
