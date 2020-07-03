import sys

from _wagyu import Box
from hypothesis import given

from . import strategies


@given(strategies.boxes)
def test_basic(box: Box) -> None:
    result = repr(box)

    assert result.startswith(Box.__module__)
    assert Box.__qualname__ in result


@given(strategies.boxes)
def test_round_trip(box: Box) -> None:
    result = repr(box)

    assert eval(result, sys.modules) == box
