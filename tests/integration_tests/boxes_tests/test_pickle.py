from hypothesis import given

from tests.utils import (BoundPortedBoxesPair,
                         are_bound_ported_boxes_equal,
                         pickle_round_trip)
from . import strategies


@given(strategies.boxes_pairs)
def test_round_trip(boxes_pair: BoundPortedBoxesPair) -> None:
    bound, ported = boxes_pair

    assert are_bound_ported_boxes_equal(pickle_round_trip(bound),
                                        pickle_round_trip(ported))
