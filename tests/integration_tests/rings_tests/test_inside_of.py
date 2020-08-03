import pytest
from hypothesis import given

from tests.utils import (BoundPortedRingsPair,
                         equivalence)
from . import strategies


@given(strategies.non_empty_rings_pairs, strategies.non_empty_rings_pairs)
def test_basic(first_pair: BoundPortedRingsPair,
               second_pair: BoundPortedRingsPair) -> None:
    first_bound, first_ported = first_pair
    second_bound, second_ported = second_pair

    try:
        bound_result = first_bound.inside_of(second_bound)
    except RuntimeError:
        with pytest.raises(RuntimeError):
            first_ported.inside_of(second_ported)
    else:
        ported_result = first_ported.inside_of(second_ported)

        assert equivalence(bound_result, ported_result)
