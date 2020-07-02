from _wagyu import Bound
from hypothesis import given

from . import strategies


@given(strategies.bounds)
def test_basic(bound: Bound) -> None:
    result = repr(bound)

    assert result.startswith(Bound.__module__)
    assert Bound.__qualname__ in result
