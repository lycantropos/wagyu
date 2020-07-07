import copy

from _wagyu import Edge
from hypothesis import given

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
