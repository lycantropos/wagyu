from _wagyu import LocalMinimumList
from hypothesis import given

from wagyu.hints import Coordinate
from . import strategies


@given(strategies.local_minimum_lists)
def test_basic(local_minimum_list: LocalMinimumList) -> None:
    assert all(isinstance(element, Coordinate)
               for element in local_minimum_list.scanbeams)


@given(strategies.local_minimum_lists)
def test_properties(local_minimum_list: LocalMinimumList) -> None:
    assert len(local_minimum_list.scanbeams) == len(local_minimum_list)
