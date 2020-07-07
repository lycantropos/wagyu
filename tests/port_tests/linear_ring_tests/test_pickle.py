from hypothesis import given

from tests.utils import pickle_round_trip
from wagyu.linear_ring import LinearRing
from . import strategies


@given(strategies.linear_rings)
def test_round_trip(linear_ring: LinearRing) -> None:
    assert pickle_round_trip(linear_ring) == linear_ring
