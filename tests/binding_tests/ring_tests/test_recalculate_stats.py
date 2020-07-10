import math

from _wagyu import Ring
from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    result = ring.recalculate_stats()

    assert result is None
    assert equivalence(math.isnan(ring.area), ring.node is None)
    assert implication(not ring.node, not ring.is_hole)
