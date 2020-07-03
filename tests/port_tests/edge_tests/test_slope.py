import math

from hypothesis import given

from tests.utils import implication
from wagyu.edge import Edge
from . import strategies


@given(strategies.edges)
def test_basic(edge: Edge) -> None:
    assert isinstance(edge.slope, float)


@given(strategies.edges)
def test_properties(edge: Edge) -> None:
    assert not math.isnan(edge.slope)
    assert implication(not edge.slope, edge.bottom.x == edge.top.x)
    assert implication(edge.bottom.y == edge.top.y, math.isinf(edge.slope))
