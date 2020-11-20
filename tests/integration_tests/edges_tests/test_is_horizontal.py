from hypothesis import given

from tests.integration_tests.utils import BoundPortedEdgesPair
from . import strategies


@given(strategies.edges_pairs)
def test_basic(edges_pair: BoundPortedEdgesPair) -> None:
    bound, ported = edges_pair

    assert bound.is_horizontal is ported.is_horizontal
