from hypothesis import strategies

from tests.strategies import coordinates
from wagyu.edge import Edge
from wagyu.point import Point

points = strategies.builds(Point, coordinates, coordinates)
edges = strategies.builds(Edge, points, points)
