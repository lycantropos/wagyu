from _wagyu import (LinearRing,
                    PolygonKind,
                    Wagyu)
from hypothesis import given

from tests.utils import equivalence
from . import strategies


@given(strategies.empty_wagyus, strategies.linear_rings,
       strategies.polygons_kinds)
def test_basic(wagyu: Wagyu,
               linear_ring: LinearRing,
               polygon_kind: PolygonKind) -> None:
    result = wagyu.add_linear_ring(linear_ring, polygon_kind)

    assert isinstance(result, bool)


@given(strategies.empty_wagyus, strategies.linear_rings,
       strategies.polygons_kinds)
def test_properties(wagyu: Wagyu,
                    linear_ring: LinearRing,
                    polygon_kind: PolygonKind) -> None:
    result = wagyu.add_linear_ring(linear_ring, polygon_kind)

    assert equivalence(result, bool(wagyu.minimums))
