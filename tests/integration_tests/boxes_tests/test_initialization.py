from typing import Tuple

from hypothesis import given

from tests.binding_tests.utils import BoundBox
from tests.integration_tests.utils import (BoundPortedPointsPair,
                                           are_bound_ported_boxes_equal)
from tests.port_tests.utils import PortedBox
from . import strategies


@given(strategies.points_pairs_pairs)
def test_basic(endpoints_pairs_pair: Tuple[BoundPortedPointsPair,
                                           BoundPortedPointsPair]) -> None:
    ((bound_minimum, ported_minimum),
     (bound_maximum, ported_maximum)) = endpoints_pairs_pair

    bound, ported = (BoundBox(bound_minimum, bound_maximum),
                     PortedBox(ported_minimum, ported_maximum))

    assert are_bound_ported_boxes_equal(bound, ported)
