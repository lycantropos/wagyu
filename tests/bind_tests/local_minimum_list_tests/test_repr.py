from _wagyu import LocalMinimumList
from hypothesis import given

from . import strategies


@given(strategies.local_minimum_lists)
def test_basic(local_minimum_list: LocalMinimumList) -> None:
    result = repr(local_minimum_list)

    assert result.startswith(LocalMinimumList.__module__)
    assert LocalMinimumList.__qualname__ in result
