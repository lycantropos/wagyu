from hypothesis import given

from tests.utils import (BoundLinearRing,
                         BoundPortedPointsListsPair,
                         PortedLinearRing,
                         are_bound_ported_points_lists_equal)
from . import strategies


@given(strategies.linear_rings_points_pairs)
def test_basic(endpoints_pairs_pair: BoundPortedPointsListsPair) -> None:
    bound_points, ported_points = endpoints_pairs_pair

    bound, ported = (BoundLinearRing(bound_points),
                     PortedLinearRing(ported_points))

    assert are_bound_ported_points_lists_equal(bound, ported)
