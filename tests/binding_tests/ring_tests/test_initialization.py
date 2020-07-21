from typing import (List,
                    Optional)

from _wagyu import (Point,
                    Ring)
from hypothesis import given

from . import strategies


@given(strategies.sizes, strategies.maybe_rings_lists, strategies.points_lists,
       strategies.booleans)
def test_basic(index: int,
               children: List[Optional[Ring]],
               points: List[Point],
               corrected: bool) -> None:
    result = Ring(index, children, points, corrected)

    assert result.index == index
    assert result.children == children
    assert result.points == points
    assert result.corrected is corrected
