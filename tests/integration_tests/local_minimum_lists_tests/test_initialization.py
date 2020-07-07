from tests.utils import (BoundLocalMinimumList,
                         PortedLocalMinimumList,
                         are_bound_ported_local_minimums_lists_equal)


def test_basic() -> None:
    bound, ported = BoundLocalMinimumList(), PortedLocalMinimumList()

    assert are_bound_ported_local_minimums_lists_equal(bound, ported)
