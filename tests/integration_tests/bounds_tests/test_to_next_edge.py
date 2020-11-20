from typing import List

from hypothesis import given

from tests.integration_tests.utils import (BoundPortedBoundsPair,
                                           are_bound_ported_bounds_equal)
from wagyu.hints import Coordinate
from . import strategies


@given(strategies.initialized_bounds_pairs, strategies.coordinates_lists)
def test_basic(pair: BoundPortedBoundsPair,
               scanbeams: List[Coordinate]) -> None:
    bound, ported = pair
    bound_scanbeams, ported_scanbeams = scanbeams, scanbeams[:]

    bound_scanbeams = bound.to_next_edge(bound_scanbeams)
    ported.to_next_edge(ported_scanbeams)

    assert bound_scanbeams == ported_scanbeams
    assert are_bound_ported_bounds_equal(bound, ported)
