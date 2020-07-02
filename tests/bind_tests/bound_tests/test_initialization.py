from _wagyu import (Bound,
                    EdgeSide,
                    Point,
                    PolygonKind)


def test_basic() -> None:
    result = Bound()

    assert result.edges == []
    assert result.last_point == Point(0, 0)
    assert result.ring is None
    assert result.maximum_bound is None
    assert result.current_x == 0.
    assert result.position == 0
    assert result.winding_count == 0
    assert result.opposite_winding_count == 0
    assert result.winding_delta == 0
    assert result.polygon_kind == PolygonKind.SUBJECT
    assert result.side == EdgeSide.LEFT
