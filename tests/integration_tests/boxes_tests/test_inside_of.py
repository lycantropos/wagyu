from hypothesis import given

from tests.integration_tests.utils import BoundPortedBoxesPair
from tests.utils import equivalence
from . import strategies


@given(strategies.boxes_pairs, strategies.boxes_pairs)
def test_basic(first_pair: BoundPortedBoxesPair,
               second_pair: BoundPortedBoxesPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    assert equivalence(first_bound.inside_of(second_bound),
                       first_ported.inside_of(second_ported))
