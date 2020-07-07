from hypothesis import given

from tests.utils import (BoundPortedLinearRingsPair,
                         are_bound_ported_points_lists_equal,
                         pickle_round_trip)
from . import strategies


@given(strategies.linear_rings_pairs)
def test_round_trip(linear_rings_pair: BoundPortedLinearRingsPair) -> None:
    bound, ported = linear_rings_pair

    assert are_bound_ported_points_lists_equal(pickle_round_trip(bound),
                                               pickle_round_trip(ported))
