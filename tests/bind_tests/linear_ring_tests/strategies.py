from typing import List

from _wagyu import (LinearRing,
                    Point)
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates
from tests.utils import RawPointsList


def to_linear_rings_points(raw_points: RawPointsList) -> List[Point]:
    points = [Point(x, y) for x, y in raw_points]
    return points + [points[0]]


linear_rings_points = planar.contours(coordinates).map(to_linear_rings_points)
linear_rings = strategies.builds(LinearRing, linear_rings_points)
