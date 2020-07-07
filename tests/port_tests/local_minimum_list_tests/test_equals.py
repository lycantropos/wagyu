from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.local_minimum import LocalMinimumList
from . import strategies


@given(strategies.local_minimum_lists)
def test_reflexivity(local_minimum_list: LocalMinimumList) -> None:
    assert local_minimum_list == local_minimum_list


@given(strategies.local_minimum_lists,
       strategies.local_minimum_lists)
def test_symmetry(first_local_minimum_list: LocalMinimumList,
                  second_local_minimum_list: LocalMinimumList) -> None:
    assert equivalence(first_local_minimum_list == second_local_minimum_list,
                       second_local_minimum_list == first_local_minimum_list)


@given(strategies.local_minimum_lists, strategies.local_minimum_lists,
       strategies.local_minimum_lists)
def test_transitivity(first_local_minimum_list: LocalMinimumList,
                      second_local_minimum_list: LocalMinimumList,
                      third_local_minimum_list: LocalMinimumList) -> None:
    assert implication(
            first_local_minimum_list == second_local_minimum_list
            and second_local_minimum_list == third_local_minimum_list,
            first_local_minimum_list == third_local_minimum_list)


@given(strategies.local_minimum_lists, strategies.local_minimum_lists)
def test_connection_with_inequality(first_local_minimum_list: LocalMinimumList,
                                    second_local_minimum_list: LocalMinimumList
                                    ) -> None:
    assert equivalence(
            not first_local_minimum_list == second_local_minimum_list,
            first_local_minimum_list != second_local_minimum_list)
