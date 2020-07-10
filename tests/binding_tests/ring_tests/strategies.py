from _wagyu import (Box,
                    Point,
                    Ring)
from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              sizes)
from tests.utils import to_maybe

booleans = strategies.booleans()
floats = floats
sizes = sizes
points = strategies.builds(Point, coordinates, coordinates)
boxes = strategies.builds(Box, points, points)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings_lists, booleans)
