import copy

from hypothesis import given

from tests.utils import (BoundPortedLinearRingsPair,
                         are_bound_ported_points_lists_equal)
from . import strategies


@given(strategies.linear_rings_pairs)
def test_shallow(linear_rings_pair: BoundPortedLinearRingsPair) -> None:
    bound, ported = linear_rings_pair

    assert are_bound_ported_points_lists_equal(copy.copy(bound),
                                               copy.copy(ported))


@given(strategies.linear_rings_pairs)
def test_deep(linear_rings_pair: BoundPortedLinearRingsPair) -> None:
    bound, ported = linear_rings_pair

    assert are_bound_ported_points_lists_equal(copy.deepcopy(bound),
                                               copy.deepcopy(ported))
