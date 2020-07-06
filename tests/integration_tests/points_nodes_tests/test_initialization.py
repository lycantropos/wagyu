from hypothesis import given

from tests.utils import (BoundPointNode,
                         PortedPointNode,
                         are_bound_ported_points_nodes_equal)
from . import strategies


@given(strategies.coordinates, strategies.coordinates)
def test_basic(x: float, y: float) -> None:
    bound, ported = BoundPointNode(x, y), PortedPointNode(x, y)

    assert are_bound_ported_points_nodes_equal(bound, ported)
