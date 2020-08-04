import pytest
from hypothesis import given

from tests.utils import (BoundPortedRingManagersPair,
                         are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs)
def test_basic(pair: BoundPortedRingManagersPair) -> None:
    bound, ported = pair

    try:
        bound.correct_tree()
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported.correct_tree()
    else:
        ported.correct_tree()

        assert are_bound_ported_ring_managers_equal(bound, ported)
