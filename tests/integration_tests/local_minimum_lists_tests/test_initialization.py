from tests.binding_tests.utils import BoundLocalMinimumList
from tests.integration_tests.utils import (
    are_bound_ported_local_minimums_lists_equal)
from tests.port_tests.utils import PortedLocalMinimumList


def test_basic() -> None:
    bound, ported = BoundLocalMinimumList(), PortedLocalMinimumList()

    assert are_bound_ported_local_minimums_lists_equal(bound, ported)
