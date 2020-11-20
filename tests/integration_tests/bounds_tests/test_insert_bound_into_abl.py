from _wagyu import insert_bound_into_abl as bound
from hypothesis import given

from tests.integration_tests.utils import (BoundPortedBoundsListsPair,
                                           BoundPortedBoundsPair,
                                           are_bound_ported_bounds_lists_equal)
from wagyu.bound import insert_bound_into_abl as ported
from . import strategies


@given(strategies.initialized_bounds_pairs,
       strategies.initialized_bounds_pairs,
       strategies.initialized_bounds_lists_pairs)
def test_basic(first_pair: BoundPortedBoundsPair,
               second_pair: BoundPortedBoundsPair,
               lists_pair: BoundPortedBoundsListsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair
    bound_list, ported_list = lists_pair

    bound_list, bound_result = bound(first_bound, second_bound, bound_list)
    ported_result = ported(first_ported, second_ported, ported_list)

    assert bound_result == ported_result
    assert are_bound_ported_bounds_lists_equal(bound_list, ported_list)
