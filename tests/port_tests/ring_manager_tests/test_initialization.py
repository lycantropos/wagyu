from typing import (List,
                    Optional)

from hypothesis import given

from wagyu.ring_manager import (Point,
                                Ring,
                                RingManager)
from . import strategies


@given(strategies.maybe_rings_lists, strategies.points_lists,
       strategies.rings_lists, strategies.non_negative_integers)
def test_basic(children: List[Optional[Ring]],
               hot_pixels: List[Point],
               rings: List[Ring],
               index: int) -> None:
    result = RingManager(children, hot_pixels, rings, index)

    assert result.children == children
    assert result.hot_pixels == hot_pixels
    assert result.rings == rings
    assert result.index == index
