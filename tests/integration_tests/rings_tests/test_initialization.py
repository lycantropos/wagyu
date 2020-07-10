from hypothesis import given

from tests.utils import (BoundPortedMaybeRingsListsPair,
                         BoundRing,
                         PortedRing,
                         are_bound_ported_rings_equal)
from . import strategies


@given(strategies.sizes, strategies.maybe_rings_lists_pairs,
       strategies.booleans)
def test_basic(index: int,
               children_pairs: BoundPortedMaybeRingsListsPair,
               corrected: bool) -> None:
    bound_children, ported_children = children_pairs

    bound, ported = (BoundRing(index, bound_children, corrected),
                     PortedRing(index, ported_children, corrected))

    assert are_bound_ported_rings_equal(bound, ported)
