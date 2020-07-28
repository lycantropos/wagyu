from collections import abc
from typing import List

from reprit.base import generate_repr

from .edge import (Edge,
                   are_edges_slopes_equal)
from .point import (Point,
                    are_points_slopes_equal,
                    is_point_between_others)


class LinearRing(abc.Sequence):
    __slots__ = 'points',

    def __init__(self, points: List[Point]) -> None:
        self.points = points

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'LinearRing') -> bool:
        return (self.points == other.points
                if isinstance(other, LinearRing)
                else NotImplemented)

    def __getitem__(self, index: int) -> Point:
        return self.points[index]

    def __len__(self) -> int:
        return len(self.points)

    @property
    def edges(self) -> List[Edge]:
        result = []  # type: List[Edge]
        if len(self) < 3:
            return result
        index = 0
        reversed_index = len(self) - 1
        pt1, pt2 = self[reversed_index], self[index]
        while pt1 == pt2:
            reversed_index -= 1
            try:
                pt1 = self[reversed_index]
            except IndexError:
                return result
        index += 1
        pt3 = self[index]
        front_pt = back_pt = None
        last_reversed_index = reversed_index + 1
        while True:
            if pt2 == pt3:
                if index == last_reversed_index:
                    break
                index += 1
                if index == last_reversed_index:
                    if not result:
                        break
                    pt3 = front_pt
                else:
                    pt3 = self[index]
                continue

            if are_points_slopes_equal(pt1, pt2, pt3):
                pt2 = pt1
                if result:
                    del result[-1]
                if result:
                    back_top = result[-1].top
                    if back_pt.x == back_top.x and back_pt.y == back_top.y:
                        pt1 = result[-1].bottom
                    else:
                        pt1 = back_top
                    back_pt = pt1
                else:
                    while self[reversed_index] == pt2:
                        reversed_index -= 1
                        if index == reversed_index:
                            return result
                    pt1 = self[reversed_index]
                    last_reversed_index = reversed_index + 1
                continue

            if not result:
                front_pt = pt2
            result.append(Edge(pt2, pt3))
            back_pt = pt2
            if index == last_reversed_index:
                break
            pt1, pt2 = pt2, pt3
            index += 1
            if index == last_reversed_index:
                if not result:
                    break
                pt3 = front_pt
            else:
                pt3 = self[index]

        modified = True
        while modified:
            modified = False
            if len(result) < 3:
                return result
            f, b = result[0], result[-1]
            if are_edges_slopes_equal(f, b):
                if f.bottom == b.top:
                    if f.top == b.bottom:
                        del result[-1]
                        del result[0]
                    else:
                        f.bottom = b.bottom
                        del result[-1]
                    modified = True
                elif f.top == b.bottom:
                    f.top = b.top
                    del result[-1]
                    modified = True
                elif f.top == b.top and f.bottom == b.bottom:
                    del result[-1]
                    del result[0]
                    modified = True
                elif f.top == b.top:
                    if is_point_between_others(f.top, f.bottom, b.bottom):
                        b.top = f.bottom
                        del result[0]
                    else:
                        f.top = b.bottom
                        del result[-1]
                    modified = True
                elif f.bottom == b.bottom:
                    if is_point_between_others(f.bottom, f.top, b.top):
                        b.bottom = f.top
                        del result[0]
                    else:
                        f.bottom = b.top
                        del result[-1]
                    modified = True
        return result
