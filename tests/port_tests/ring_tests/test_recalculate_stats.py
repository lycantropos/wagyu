import math

from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.ring import Ring
from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    result = ring.recalculate_stats()

    assert result is None
    assert equivalence(math.isnan(ring.area), ring.node is None)
    assert implication(ring.node is None, not ring.is_hole)
