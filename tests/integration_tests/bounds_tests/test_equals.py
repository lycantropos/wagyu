from hypothesis import given

from tests.integration_tests.utils import BoundPortedBoundsPair
from tests.utils import equivalence
from . import strategies


@given(strategies.bounds_pairs, strategies.bounds_pairs)
def test_basic(first_pair: BoundPortedBoundsPair,
               second_pair: BoundPortedBoundsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
