from _wagyu import (Box,
                    Point)
from hypothesis import strategies

from tests.strategies import coordinates

points = strategies.builds(Point, coordinates, coordinates)
boxes = strategies.builds(Box, points, points)
