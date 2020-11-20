import pytest
from hypothesis import given

from tests.integration_tests.utils import (
    BoundPortedRingManagersPair,
    are_bound_ported_ring_managers_equal)
from . import strategies


@given(strategies.ring_managers_pairs)
def test_basic(pair: BoundPortedRingManagersPair) -> None:
    bound, ported = pair

    try:
        bound.correct_topology()
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported.correct_topology()
    else:
        ported.correct_topology()

        assert are_bound_ported_ring_managers_equal(bound, ported)
