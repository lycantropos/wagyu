from typing import (List,
                    Optional)

from _wagyu import (Point,
                    Ring,
                    RingManager)
from hypothesis import given

from . import strategies


@given(strategies.maybe_rings_lists, strategies.points_lists, strategies.sizes,
       strategies.rings_lists, strategies.sizes)
def test_basic(children: List[Optional[Ring]],
               hot_pixels: List[Point],
               current_hot_pixels_index: int,
               rings: List[Ring],
               index: int) -> None:
    result = RingManager(children, hot_pixels, current_hot_pixels_index,
                         rings, index)

    assert result.children == children
    assert result.hot_pixels == hot_pixels
    assert result.current_hot_pixels_index == min(current_hot_pixels_index,
                                                  len(hot_pixels))
    assert result.rings == rings
    assert result.index == index
