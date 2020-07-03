from _wagyu import (Edge,
                    Point)
from hypothesis import strategies

from tests.strategies import coordinates

points = strategies.builds(Point, coordinates, coordinates)
edges = strategies.builds(Edge, points, points)
