from hypothesis import given

from tests.utils import (BoundPortedRingsPair,
                         equivalence)
from . import strategies


@given(strategies.rings_pairs, strategies.rings_pairs)
def test_basic(first_rings_pair: BoundPortedRingsPair,
               second_rings_pair: BoundPortedRingsPair) -> None:
    first_bound, first_ported = first_rings_pair
    second_bound, second_ported = second_rings_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
