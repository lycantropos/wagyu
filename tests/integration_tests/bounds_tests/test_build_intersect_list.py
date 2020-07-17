import pytest
from _wagyu import build_intersect_list as bound
from hypothesis import given

from tests.utils import (BoundPortedBoundsListsPair,
                         are_bound_ported_bounds_lists_equal,
                         are_bound_ported_intersect_nodes_lists_equal)
from wagyu.intersect_node import build_intersect_list as ported
from . import strategies


@given(strategies.initialized_bounds_lists_pairs)
def test_basic(lists_pair: BoundPortedBoundsListsPair) -> None:
    bound_list, ported_list = lists_pair

    assert are_bound_ported_bounds_lists_equal(bound_list, ported_list)

    try:
        bound_list, bound_result = bound(bound_list)
    except RuntimeError:
        with pytest.raises(RuntimeError):
            ported(ported_list)
    else:
        ported_list, ported_result = ported(ported_list)

        assert are_bound_ported_bounds_lists_equal(bound_list, ported_list)
        assert are_bound_ported_intersect_nodes_lists_equal(bound_result,
                                                            ported_result)
