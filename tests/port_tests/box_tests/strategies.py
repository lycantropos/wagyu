from hypothesis import strategies

from tests.strategies import coordinates
from wagyu.box import Box
from wagyu.point import Point

points = strategies.builds(Point, coordinates, coordinates)
boxes = strategies.builds(Box, points, points)
