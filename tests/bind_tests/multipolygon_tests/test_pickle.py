from _wagyu import Multipolygon
from hypothesis import given

from tests.utils import pickle_round_trip
from . import strategies


@given(strategies.multipolygons)
def test_round_trip(multipolygon: Multipolygon) -> None:
    assert pickle_round_trip(multipolygon) == multipolygon
