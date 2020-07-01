from _wagyu import (Box,
                    Point)
from hypothesis import strategies

from tests.strategies import floats

points = strategies.builds(Point, floats, floats)
boxes = strategies.builds(Box, points, points)
