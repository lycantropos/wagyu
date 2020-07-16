from hypothesis import given

from tests.utils import (BoundPortedLocalMinimumListsPair,
                         BoundPortedRingManagersPair,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs, strategies.local_minimum_lists_pairs)
def test_basic(pair: BoundPortedRingManagersPair,
               local_minimum_lists_pair: BoundPortedLocalMinimumListsPair
               ) -> None:
    bound, ported = pair
    (bound_local_minimum_list,
     ported_local_minimum_list) = local_minimum_lists_pair

    bound.build_hot_pixels(bound_local_minimum_list)
    ported.build_hot_pixels(ported_local_minimum_list)

    assert are_bound_ported_ring_managers_equal(bound, ported)
