import ctypes
import math
import struct
from bisect import bisect_left
from decimal import (ROUND_HALF_UP,
                     Decimal)
from typing import (Callable,
                    MutableSequence,
                    Sequence)

from .hints import (Coordinate,
                    Domain)


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


def find_if(predicate: Callable[[Domain], bool],
            values: Sequence[Domain]) -> int:
    """
    Equivalent of C++'s ``std::find_if``.
    """
    for index, value in enumerate(values):
        if predicate(value):
            return index
    return len(values)


def round_towards_min(value: Coordinate) -> Coordinate:
    return (math.floor(value)
            if are_floats_almost_equal(math.floor(value) + 0.5, value)
            else round_half_up(value))


def round_towards_max(value: Coordinate) -> Coordinate:
    return (math.ceil(value)
            if are_floats_almost_equal(math.floor(value) + 0.5, value)
            else round_half_up(value))


def round_half_up(number: Coordinate) -> int:
    """
    Equivalent of C++'s ``std::llround``.
    """
    return int(Decimal(number).quantize(0, ROUND_HALF_UP))
