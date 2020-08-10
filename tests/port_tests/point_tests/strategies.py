from hypothesis import strategies

from tests.strategies import coordinates
from wagyu.point import Point

points = strategies.builds(Point, coordinates, coordinates)
