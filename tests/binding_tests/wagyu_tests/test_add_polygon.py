from _wagyu import (LinearRing,
                    PolygonKind,
                    Wagyu)
from hypothesis import given

from tests.utils import equivalence
from . import strategies


@given(strategies.empty_wagyus, strategies.polygons, strategies.polygons_kinds)
def test_basic(wagyu: Wagyu,
               polygon: LinearRing,
               polygon_kind: PolygonKind) -> None:
    result = wagyu.add_polygon(polygon, polygon_kind)

    assert isinstance(result, bool)


@given(strategies.empty_wagyus, strategies.polygons, strategies.polygons_kinds)
def test_properties(wagyu: Wagyu,
                    polygon: LinearRing,
                    polygon_kind: PolygonKind) -> None:
    result = wagyu.add_polygon(polygon, polygon_kind)

    assert equivalence(result, bool(wagyu.minimums))
