import math

from hypothesis import given

from tests.utils import equivalence
from wagyu.ring import Ring
from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    assert isinstance(ring.area, float)


@given(strategies.rings)
def test_properties(ring: Ring) -> None:
    assert equivalence(ring.node is None, math.isnan(ring.area))
