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

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from wagyu.hints import Coordinate

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy
RawPoint = Tuple[Coordinate, Coordinate]
RawPointsList = List[RawPoint]
RawPolygon = Tuple[RawPointsList, List[RawPointsList]]
RawMultipolygon = List[RawPolygon]


def enum_to_values(cls: Type[Enum]) -> List[Enum]:
    return [value for _, value in sorted(cls.__members__.items())]


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
