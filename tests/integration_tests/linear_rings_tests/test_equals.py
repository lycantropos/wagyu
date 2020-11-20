from hypothesis import given

from tests.integration_tests.utils import BoundPortedLinearRingsPair
from tests.utils import equivalence
from . import strategies


@given(strategies.linear_rings_pairs, strategies.linear_rings_pairs)
def test_basic(first_pair: BoundPortedLinearRingsPair,
               second_pair: BoundPortedLinearRingsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
