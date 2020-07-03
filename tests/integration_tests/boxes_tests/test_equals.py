from hypothesis import given

from tests.utils import (BoundPortedBoxesPair,
                         equivalence)
from . import strategies


@given(strategies.boxes_pairs, strategies.boxes_pairs)
def test_basic(first_boxes_pair: BoundPortedBoxesPair,
               second_boxes_pair: BoundPortedBoxesPair) -> None:
    first_bound, first_ported = first_boxes_pair
    second_bound, second_ported = second_boxes_pair

    assert equivalence(first_bound == second_bound,
                       first_ported == second_ported)
