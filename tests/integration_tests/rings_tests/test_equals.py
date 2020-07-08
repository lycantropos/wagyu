from hypothesis import given

from tests.utils import (BoundPortedRingsPair,
                         equivalence)
from . import strategies


@given(strategies.rings_pairs, strategies.rings_pairs)
def test_basic(first_edges_pair: BoundPortedRingsPair,
               second_edges_pair: BoundPortedRingsPair) -> None:
    first_bound, first_ported = first_edges_pair
    second_bound, second_ported = second_edges_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
