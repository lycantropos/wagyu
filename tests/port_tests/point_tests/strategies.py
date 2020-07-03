from wagyu.point import Point
from hypothesis import strategies

from tests.strategies import coordinates

points = strategies.builds(Point, coordinates, coordinates)
