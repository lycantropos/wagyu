from hypothesis import given

from tests.utils import (BoundPortedEdgesPair,
                         are_bound_ported_edges_equal)
from . import strategies


@given(strategies.edges_pairs)
def test_basic(edges_pair: BoundPortedEdgesPair) -> None:
    bound, ported = edges_pair

    bound.reverse_horizontal()
    ported.reverse_horizontal()

    assert are_bound_ported_edges_equal(bound, ported)
