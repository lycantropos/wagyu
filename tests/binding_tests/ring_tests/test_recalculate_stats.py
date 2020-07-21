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
    assert equivalence(math.isnan(ring.area), not ring.points)
    assert implication(not ring.points, not ring.is_hole)
