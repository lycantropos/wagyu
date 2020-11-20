import copy

from hypothesis import given

from tests.integration_tests.utils import (BoundPortedBoxesPair,
                                           are_bound_ported_boxes_equal)
from . import strategies


@given(strategies.boxes_pairs)
def test_shallow(boxes_pair: BoundPortedBoxesPair) -> None:
    bound, ported = boxes_pair

    assert are_bound_ported_boxes_equal(copy.copy(bound), copy.copy(ported))


@given(strategies.boxes_pairs)
def test_deep(boxes_pair: BoundPortedBoxesPair) -> None:
    bound, ported = boxes_pair

    assert are_bound_ported_boxes_equal(copy.deepcopy(bound),
                                        copy.deepcopy(ported))
