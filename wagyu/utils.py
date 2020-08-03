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


def are_floats_greater_than_or_equal(x: float, y: float) -> bool:
    return x > y or are_floats_almost_equal(x, y)


def are_floats_greater_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x > y


def are_floats_less_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x < y


def is_float_almost_zero(value: float) -> bool:
    return are_floats_almost_equal(value, 0.)


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


def find(value: Domain, sequence: Sequence[Domain]) -> int:
    """
    Equivalent of C++'s ``std::find``.
    """
    return next((index
                 for index, element in enumerate(sequence)
                 if element is value),
                len(sequence))


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


def is_odd(number: int) -> bool:
    return bool(number % 2)


def quicksort(sequence: MutableSequence[Domain],
              comparator: Callable[[Domain, Domain], bool]) -> None:
    _quicksort(sequence, 0, len(sequence) - 1, comparator)


def _quicksort(sequence: MutableSequence[Domain],
               start: int,
               end: int,
               comparator: Callable[[Domain, Domain], bool]) -> None:
    if start >= end:
        return
    pivot = partition(sequence, start, end, comparator)
    _quicksort(sequence, start, pivot - 1, comparator)
    _quicksort(sequence, pivot + 1, end, comparator)


def partition(sequence: MutableSequence[Domain],
              start: int,
              end: int,
              comparator: Callable[[Domain, Domain], bool]) -> int:
    pivot = sequence[start]
    low = start + 1
    high = end
    while True:
        while low <= high and comparator(sequence[high], pivot):
            high = high - 1
        while low <= high and not comparator(sequence[low], pivot):
            low = low + 1
        if low <= high:
            sequence[low], sequence[high] = sequence[high], sequence[low]
        else:
            break
    sequence[start], sequence[high] = sequence[high], sequence[start]
    return high
