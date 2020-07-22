from _wagyu import (LinearRing,
                    LocalMinimumList,
                    PolygonKind)
from hypothesis import given

from tests.utils import equivalence
from . import strategies


@given(strategies.local_minimum_lists, strategies.linear_rings,
       strategies.polygon_kinds)
def test_basic(local_minimum_list: LocalMinimumList,
               linear_ring: LinearRing,
               polygon_kind: PolygonKind) -> None:
    result = local_minimum_list.add_linear_ring(linear_ring, polygon_kind)

    assert isinstance(result, bool)


@given(strategies.local_minimum_lists, strategies.linear_rings,
       strategies.polygon_kinds)
def test_properties(local_minimum_list: LocalMinimumList,
                    linear_ring: LinearRing,
                    polygon_kind: PolygonKind) -> None:
    result = local_minimum_list.add_linear_ring(linear_ring, polygon_kind)

    assert equivalence(result, bool(local_minimum_list))
