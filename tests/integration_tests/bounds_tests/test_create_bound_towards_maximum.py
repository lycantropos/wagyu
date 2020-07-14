from _wagyu import create_bound_towards_maximum as bound
from hypothesis import given

from tests.utils import (BoundPortedEdgesListsPair,
                         are_bound_ported_bounds_equal)
from wagyu.bound import create_bound_towards_maximum as ported
from . import strategies


@given(strategies.edges_lists_pairs)
def test_basic(edges_lists_pair: BoundPortedEdgesListsPair) -> None:
    bound_edges, ported_edges = edges_lists_pair

    assert are_bound_ported_bounds_equal(bound(bound_edges),
                                         ported(ported_edges))
