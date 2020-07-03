from hypothesis import given

from tests.utils import pickle_round_trip
from wagyu.box import Box
from . import strategies


@given(strategies.boxes)
def test_round_trip(box: Box) -> None:
    assert pickle_round_trip(box) == box
