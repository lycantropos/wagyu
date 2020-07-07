from _wagyu import are_edges_slopes_equal as bound
from hypothesis import given

from tests.utils import BoundPortedEdgesPair, equivalence
from wagyu.utils import are_edges_slopes_equal as ported
from . import strategies


@given(strategies.edges_pairs, strategies.edges_pairs)
def test_basic(first_edges_pair: BoundPortedEdgesPair,
               second_edges_pair: BoundPortedEdgesPair) -> None:
    bound_first, ported_first = first_edges_pair
    bound_second, ported_second = second_edges_pair

    assert equivalence(ported(ported_first, ported_second),
                       bound(bound_first, bound_second))
