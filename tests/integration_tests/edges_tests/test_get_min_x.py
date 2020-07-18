from hypothesis import given

from tests.utils import BoundPortedEdgesPair
from . import strategies


@given(strategies.edges_pairs, strategies.floats)
def test_basic(pair: BoundPortedEdgesPair, current_y: float) -> None:
    bound, ported = pair

    assert bound.get_min_x(current_y) == ported.get_min_x(current_y)
