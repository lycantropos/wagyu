from hypothesis import given

from tests.utils import (BoundPortedLocalMinimumsPair,
                         equivalence)
from . import strategies


@given(strategies.local_minimums_pairs,
       strategies.local_minimums_pairs)
def test_basic(first_pair: BoundPortedLocalMinimumsPair,
               second_pair: BoundPortedLocalMinimumsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
