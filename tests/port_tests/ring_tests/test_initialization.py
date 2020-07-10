from typing import (List,
                    Optional)

from hypothesis import given

from wagyu.ring import Ring
from . import strategies


@given(strategies.non_negative_integers, strategies.maybe_rings_lists,
       strategies.booleans)
def test_basic(index: int,
               children: List[Optional[Ring]],
               corrected: bool) -> None:
    result = Ring(index, children, corrected)

    assert result.index == index
    assert result.children == children
    assert result.corrected is corrected
