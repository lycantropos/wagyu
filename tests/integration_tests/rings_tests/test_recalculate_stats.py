import math

from hypothesis import given

from tests.integration_tests.utils import (BoundPortedRingsPair,
                                           are_bound_ported_boxes_equal)
from . import strategies


@given(strategies.rings_pairs)
def test_basic(rings_pair: BoundPortedRingsPair) -> None:
    bound, ported = rings_pair

    bound.recalculate_stats()
    ported.recalculate_stats()

    assert (math.isnan(bound.area) and math.isnan(ported.area)
            or bound.area == ported.area)
    assert bound.size == ported.size
    assert are_bound_ported_boxes_equal(bound.box, ported.box)
    assert bound.is_hole == ported.is_hole
