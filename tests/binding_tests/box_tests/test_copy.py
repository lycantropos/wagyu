import copy

from _wagyu import Box
from hypothesis import given

from . import strategies


@given(strategies.boxes)
def test_shallow(box: Box) -> None:
    result = copy.copy(box)

    assert result is not box
    assert result == box


@given(strategies.boxes)
def test_deep(box: Box) -> None:
    result = copy.deepcopy(box)

    assert result is not box
    assert result == box
