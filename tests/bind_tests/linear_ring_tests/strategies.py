from typing import (List,
                    Tuple)

from _wagyu import (LinearRing,
                    Point)
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from wagyu.hints import Coordinate


def to_linear_ring_points(raw_points: List[Tuple[Coordinate, Coordinate]]
                          ) -> List[Point]:
    points = [Point(x, y) for x, y in raw_points]
    return points + [points[0]]


linear_rings_points = planar.contours(coordinates).map(to_linear_ring_points)
linear_rings = strategies.builds(LinearRing, linear_rings_points)
