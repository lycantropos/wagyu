from hypothesis import given

from tests.integration_tests.utils import BoundPortedLocalMinimumListsPair
from . import strategies


@given(strategies.local_minimum_lists_pairs)
def test_basic(pair: BoundPortedLocalMinimumListsPair) -> None:
    bound, ported = pair

    assert bound.scanbeams == ported.scanbeams
