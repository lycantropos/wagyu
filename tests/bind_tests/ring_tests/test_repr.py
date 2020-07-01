import sys

from _wagyu import Ring
from hypothesis import given

from . import strategies


@given(strategies.rings)
def test_basic(ring: Ring) -> None:
    result = repr(ring)

    assert result.startswith(Ring.__module__)
    assert Ring.__qualname__ in result


@given(strategies.rings)
def test_round_trip(ring: Ring) -> None:
    result = repr(ring)

    assert eval(result, sys.modules) == ring
