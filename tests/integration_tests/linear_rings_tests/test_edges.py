from hypothesis import given

from tests.integration_tests.utils import (BoundPortedLinearRingsPair,
                                           are_bound_ported_edges_lists_equal)
from . import strategies


@given(strategies.linear_rings_pairs)
def test_basic(linear_rings_pair: BoundPortedLinearRingsPair) -> None:
    bound, ported = linear_rings_pair

    assert are_bound_ported_edges_lists_equal(bound.edges, ported.edges)
