import pickle
from typing import (Optional,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def pickle_round_trip(object_: Domain) -> Domain:
    return pickle.loads(pickle.dumps(object_))


def to_maybe(strategy: Strategy[Domain]) -> Strategy[Optional[Domain]]:
    return strategies.none() | strategy
