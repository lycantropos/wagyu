from hypothesis import given

from tests.utils import (BoundPortedMaybeRingsListsPair,
                         BoundPortedPointsNodesPair,
                         BoundRing,
                         PortedRing,
                         are_bound_ported_rings_equal)
from . import strategies


@given(strategies.sizes, strategies.maybe_rings_lists_pairs,
       strategies.maybe_points_nodes_pairs,
       strategies.maybe_points_nodes_pairs, strategies.booleans)
def test_basic(index: int,
               children_pairs: BoundPortedMaybeRingsListsPair,
               nodes_pairs: BoundPortedPointsNodesPair,
               bottom_nodes_pairs: BoundPortedPointsNodesPair,
               corrected: bool) -> None:
    bound_children, ported_children = children_pairs
    bound_node, ported_node = nodes_pairs
    bound_bottom_node, ported_bottom_node = bottom_nodes_pairs

    bound, ported = (BoundRing(index, bound_children, bound_node,
                               bound_bottom_node, corrected),
                     PortedRing(index, ported_children, ported_node,
                                ported_bottom_node, corrected))

    assert are_bound_ported_rings_equal(bound, ported)
