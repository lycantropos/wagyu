from _wagyu import round_towards_max as bound
from hypothesis import given

from wagyu.utils import round_towards_max as ported
from . import strategies


@given(strategies.floats)
def test_basic(value: float) -> None:
    assert bound(value) == ported(value)
