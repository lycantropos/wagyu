from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.bound import Bound
from . import strategies


@given(strategies.bounds)
def test_reflexivity(bound: Bound) -> None:
    assert bound == bound


@given(strategies.bounds, strategies.bounds)
def test_symmetry(first_bound: Bound,
                  second_bound: Bound) -> None:
    assert equivalence(first_bound == second_bound,
                       second_bound == first_bound)


@given(strategies.bounds, strategies.bounds,
       strategies.bounds)
def test_transitivity(first_bound: Bound,
                      second_bound: Bound,
                      third_bound: Bound) -> None:
    assert implication(first_bound == second_bound
                       and second_bound == third_bound,
                       first_bound == third_bound)


@given(strategies.bounds, strategies.bounds)
def test_connection_with_inequality(first_bound: Bound,
                                    second_bound: Bound) -> None:
    assert equivalence(not first_bound == second_bound,
                       first_bound != second_bound)
