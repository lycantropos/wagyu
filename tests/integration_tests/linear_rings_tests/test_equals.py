from hypothesis import given

from tests.utils import (BoundPortedLinearRingsPair,
                         equivalence)
from . import strategies


@given(strategies.linear_rings_pairs, strategies.linear_rings_pairs)
def test_basic(first_linear_rings_pair: BoundPortedLinearRingsPair,
               second_linear_rings_pair: BoundPortedLinearRingsPair) -> None:
    first_bound, first_ported = first_linear_rings_pair
    second_bound, second_ported = second_linear_rings_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
