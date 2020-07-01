from _wagyu import (Edge,
                    Point)
from hypothesis import strategies

from tests.strategies import floats

points = strategies.builds(Point, floats, floats)
edges = strategies.builds(Edge, points, points)
