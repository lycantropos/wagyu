import copy

from hypothesis import given

from wagyu.edge import Edge
from . import strategies


@given(strategies.edges)
def test_basic(edge: Edge) -> None:
    result = edge.reverse_horizontal()

    assert result is None


@given(strategies.edges)
def test_involution(edge: Edge) -> None:
    original = copy.deepcopy(edge)

    edge.reverse_horizontal()
    edge.reverse_horizontal()

    assert original == edge
