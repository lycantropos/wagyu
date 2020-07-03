from _wagyu import LinearRing
from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.local_minimum_lists)
def test_reflexivity(local_minimum_list: LinearRing) -> None:
    assert local_minimum_list == local_minimum_list


@given(strategies.local_minimum_lists,
       strategies.local_minimum_lists)
def test_symmetry(first_local_minimum_list: LinearRing,
                  second_local_minimum_list: LinearRing) -> None:
    assert equivalence(first_local_minimum_list == second_local_minimum_list,
                       second_local_minimum_list == first_local_minimum_list)


@given(strategies.local_minimum_lists, strategies.local_minimum_lists,
       strategies.local_minimum_lists)
def test_transitivity(first_local_minimum_list: LinearRing,
                      second_local_minimum_list: LinearRing,
                      third_local_minimum_list: LinearRing) -> None:
    assert implication(
            first_local_minimum_list == second_local_minimum_list
            and second_local_minimum_list == third_local_minimum_list,
            first_local_minimum_list == third_local_minimum_list)


@given(strategies.local_minimum_lists, strategies.local_minimum_lists)
def test_connection_with_inequality(first_local_minimum_list: LinearRing,
                                    second_local_minimum_list: LinearRing
                                    ) -> None:
    assert equivalence(
            not first_local_minimum_list == second_local_minimum_list,
            first_local_minimum_list != second_local_minimum_list)
