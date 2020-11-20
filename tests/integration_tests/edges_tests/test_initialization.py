from typing import Tuple

from hypothesis import given

from tests.binding_tests.utils import BoundEdge
from tests.integration_tests.utils import (BoundPortedPointsPair,
                                           are_bound_ported_edges_equal)
from tests.port_tests.utils import PortedEdge
from . import strategies


@given(strategies.points_pairs_pairs)
def test_basic(endpoints_pairs_pair: Tuple[BoundPortedPointsPair,
                                           BoundPortedPointsPair]) -> None:
    ((bound_left, ported_left),
     (bound_right, ported_right)) = endpoints_pairs_pair

    bound, ported = (BoundEdge(bound_left, bound_right),
                     PortedEdge(ported_left, ported_right))

    assert are_bound_ported_edges_equal(bound, ported)
