from hypothesis import given

from tests.integration_tests.utils import BoundPortedRingManagersPair
from tests.utils import equivalence
from . import strategies


@given(strategies.ring_managers_pairs, strategies.ring_managers_pairs)
def test_basic(first_pair: BoundPortedRingManagersPair,
               second_pair: BoundPortedRingManagersPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
