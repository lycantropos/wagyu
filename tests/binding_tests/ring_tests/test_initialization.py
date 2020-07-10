from typing import (List,
                    Optional)

from _wagyu import Ring
from hypothesis import given

from . import strategies


@given(strategies.sizes, strategies.maybe_rings_lists, strategies.booleans)
def test_basic(index: int,
               children: List[Optional[Ring]],
               corrected: bool) -> None:
    result = Ring(index, children, corrected)

    assert result.index == index
    assert result.children == children
    assert result.corrected is corrected
