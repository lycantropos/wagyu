import ctypes
import struct
from bisect import bisect_left
from typing import MutableSequence

from .edge import Edge
from .hints import Domain
from .point import Point


def are_points_slopes_equal(first: Point, second: Point, third: Point) -> bool:
    return ((first.y - second.y) * (second.x - third.x)
            == (first.x - second.x) * (second.y - third.y))


def are_edges_slopes_equal(first: Edge, second: Edge) -> bool:
    return ((first.top.y - first.bottom.y) * (second.top.x - second.bottom.x)
            == ((first.top.x - first.bottom.x)
                * (second.top.y - second.bottom.y)))


def is_point_between_others(pt1: Point, pt2: Point, pt3: Point) -> bool:
    if pt1 == pt2 or pt2 == pt3 or pt1 == pt3:
        return False
    elif pt1.x != pt3.x:
        return (pt2.x > pt1.x) is (pt2.x < pt3.x)
    else:
        return (pt2.y > pt1.y) is (pt2.y < pt3.y)


def are_floats_greater_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x > y


def are_floats_less_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x < y


def are_floats_almost_equal(left: float, right: float,
                            *,
                            max_ulps: int = 4) -> bool:
    left_bits = _double_to_biased(left)
    right_bits = _double_to_biased(right)
    return abs(left_bits - right_bits) <= max_ulps


def _double_to_biased(value: float,
                      *,
                      sign_bit_mask: int = 2 ** 63) -> int:
    result, = struct.unpack('!Q', struct.pack('!d', value))
    if sign_bit_mask & result:
        return ctypes.c_uint64(~result + 1).value
    else:
        return ctypes.c_uint64(sign_bit_mask | result).value


def insort_unique(sequence: MutableSequence[Domain], value: Domain) -> None:
    index = bisect_left(sequence, value)
    if index == len(sequence) or value < sequence[index]:
        sequence.insert(index, value)
