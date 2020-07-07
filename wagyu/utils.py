from .edge import Edge
from .point import Point


def are_points_slopes_equal(first: Point, second: Point, third: Point) -> bool:
    return ((first.y - second.y) * (second.x - third.x)
            == (first.x - second.x) * (second.y - third.y))


def are_edges_slopes_equal(first: Edge, second: Edge) -> bool:
    return ((first.top.y - first.bottom.y) * (second.top.x - second.bottom.x)
            == ((first.top.x - first.bottom.x)
                * (second.top.y - second.bottom.y)))


def is_point_between_others(pt1: Point, pt2: Point, pt3: Point) -> bool:
    if pt1 == pt2 or pt2 == pt3 or pt1 == pt3:
        return False
    elif pt1.x != pt3.x:
        return (pt2.x > pt1.x) is (pt2.x < pt3.x)
    else:
        return (pt2.y > pt1.y) is (pt2.y < pt3.y)
