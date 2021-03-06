from _wagyu import are_edges_slopes_equal as bound
from hypothesis import given

from tests.integration_tests.utils import BoundPortedEdgesPair
from tests.utils import equivalence
from wagyu.edge import are_edges_slopes_equal as ported
from . import strategies


@given(strategies.edges_pairs, strategies.edges_pairs)
def test_basic(first_pair: BoundPortedEdgesPair,
               second_pair: BoundPortedEdgesPair) -> None:
    bound_first, ported_first = first_pair
    bound_second, ported_second = second_pair

    assert equivalence(ported(ported_first, ported_second),
                       bound(bound_first, bound_second))
