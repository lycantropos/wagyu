from _wagyu import Ring
from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    assert isinstance(ring.is_hole, bool)


@given(strategies.rings)
def test_properties(ring: Ring) -> None:
    assert implication(ring.node is None, not ring.is_hole)
    assert equivalence(ring.area <= 0, ring.is_hole)
