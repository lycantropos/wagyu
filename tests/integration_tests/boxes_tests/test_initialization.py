from typing import Tuple

from hypothesis import given

from tests.utils import (BoundBox,
                         BoundPortedPointsPair,
                         PortedBox,
                         are_bound_ported_boxes_equal)
from . import strategies


@given(strategies.points_pairs_pairs)
def test_basic(endpoints_pairs_pair: Tuple[BoundPortedPointsPair,
                                           BoundPortedPointsPair]) -> None:
    ((bound_minimum, ported_minimum),
     (bound_maximum, ported_maximum)) = endpoints_pairs_pair

    bound, ported = (BoundBox(bound_minimum, bound_maximum),
                     PortedBox(ported_minimum, ported_maximum))

    assert are_bound_ported_boxes_equal(bound, ported)
