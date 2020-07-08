from hypothesis import given

from tests.utils import (BoundPortedEdgesPair,
                         are_bound_ported_maybe_points_equal)
from . import strategies


@given(strategies.edges_pairs, strategies.edges_pairs)
def test_basic(first_edges_pair: BoundPortedEdgesPair,
               second_edges_pair: BoundPortedEdgesPair) -> None:
    first_bound, first_ported = first_edges_pair
    second_bound, second_ported = second_edges_pair

    assert are_bound_ported_maybe_points_equal(first_bound & second_bound,
                                               first_ported & second_ported)
