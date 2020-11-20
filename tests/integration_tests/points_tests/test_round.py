from hypothesis import given

from tests.integration_tests.utils import BoundPortedPointsPair, \
    are_bound_ported_points_equal
from . import strategies


@given(strategies.float_points_pairs)
def test_basic(points_pair: BoundPortedPointsPair) -> None:
    bound, ported = points_pair

    assert are_bound_ported_points_equal(bound.round(), ported.round())
