from hypothesis import given

from tests.integration_tests.utils import BoundPortedRingsPair
from . import strategies


@given(strategies.rings_pairs)
def test_basic(rings_pair: BoundPortedRingsPair) -> None:
    bound, ported = rings_pair

    assert bound.depth == ported.depth
