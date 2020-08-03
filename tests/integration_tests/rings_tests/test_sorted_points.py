from hypothesis import given

from tests.utils import (BoundPortedRingsPair,
                         are_bound_ported_points_lists_equal)
from wagyu.point_node import point_node_to_point
from . import strategies


@given(strategies.non_empty_rings_pairs)
def test_basic(rings_pair: BoundPortedRingsPair) -> None:
    bound, ported = rings_pair

    assert are_bound_ported_points_lists_equal(bound.sorted_points,
                                               list(map(point_node_to_point,
                                                        ported.sorted_nodes)))
