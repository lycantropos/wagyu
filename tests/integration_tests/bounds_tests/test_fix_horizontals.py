from hypothesis import given

from tests.integration_tests.utils import (BoundPortedBoundsPair,
                                           are_bound_ported_bounds_equal)
from . import strategies


@given(strategies.bounds_pairs)
def test_basic(pair: BoundPortedBoundsPair) -> None:
    bound, ported = pair

    bound.fix_horizontals()
    ported.fix_horizontals()

    assert are_bound_ported_bounds_equal(bound, ported)
