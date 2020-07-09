from hypothesis import given

from tests.utils import (BoundPortedPointsNodesPair,
                         equivalence)
from . import strategies


@given(strategies.points_nodes_pairs, strategies.points_nodes_pairs)
def test_basic(first_pair: BoundPortedPointsNodesPair,
               second_pair: BoundPortedPointsNodesPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
