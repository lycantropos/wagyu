from hypothesis import given

from tests.integration_tests.utils import (BoundPortedBoundsPair,
                                           are_bound_ported_plain_bounds_equal)
from . import strategies


@given(strategies.bounds_pairs, strategies.bounds_pairs)
def test_basic(first_pair: BoundPortedBoundsPair,
               second_pair: BoundPortedBoundsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    first_bound.move_horizontals(second_bound)
    first_ported.move_horizontals(second_ported)

    assert are_bound_ported_plain_bounds_equal(first_bound, first_ported)
    assert are_bound_ported_plain_bounds_equal(second_bound, second_ported)
