from hypothesis import given

from wagyu.local_minimum import LocalMinimumList
from . import strategies


@given(strategies.local_minimum_lists)
def test_self(local_minimum_list: LocalMinimumList) -> None:
    assert all(element in local_minimum_list for element in local_minimum_list)
