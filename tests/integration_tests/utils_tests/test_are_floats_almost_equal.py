from _wagyu import are_floats_almost_equal as bound
from hypothesis import given

from wagyu.utils import are_floats_almost_equal as ported
from . import strategies


@given(strategies.floats, strategies.floats)
def test_basic(left: float, right: float) -> None:
    assert bound(left, right) is ported(left, right)
