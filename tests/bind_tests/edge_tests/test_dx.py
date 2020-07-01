import math

from _wagyu import Edge
from hypothesis import given

from tests.utils import implication
from . import strategies


@given(strategies.edges)
def test_basic(edge: Edge) -> None:
    assert isinstance(edge.dx, float)


@given(strategies.edges)
def test_properties(edge: Edge) -> None:
    assert not math.isnan(edge.dx)
    assert implication(not edge.dx, edge.bottom.x == edge.top.x)
    assert implication(edge.bottom.y == edge.top.y, math.isinf(edge.dx))
