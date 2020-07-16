from hypothesis import given

from tests.utils import (BoundPortedIntersectNodesPair,
                         equivalence)
from . import strategies


@given(strategies.intersect_nodes_pairs, strategies.intersect_nodes_pairs)
def test_basic(first_pair: BoundPortedIntersectNodesPair,
               second_pair: BoundPortedIntersectNodesPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound < second_bound,
                       first_ported < second_ported)
