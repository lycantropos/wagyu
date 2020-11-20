from hypothesis import given

from tests.integration_tests.utils import BoundPortedLocalMinimumListsPair
from tests.utils import equivalence
from . import strategies


@given(strategies.local_minimum_lists_pairs,
       strategies.local_minimum_lists_pairs)
def test_basic(first_pair: BoundPortedLocalMinimumListsPair,
               second_pair: BoundPortedLocalMinimumListsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
