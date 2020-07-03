import copy

from hypothesis import given

from wagyu.box import Box
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
