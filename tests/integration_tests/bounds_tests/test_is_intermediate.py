from hypothesis import given

from tests.integration_tests.utils import BoundPortedBoundsPair
from tests.utils import equivalence
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.initialized_bounds_pairs, strategies.coordinates)
def test_basic(pair: BoundPortedBoundsPair, y: Coordinate) -> None:
    bound, ported = pair

    assert equivalence(bound.is_intermediate(y), ported.is_intermediate(y))
