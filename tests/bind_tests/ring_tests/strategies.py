from _wagyu import (Box,
                    Point,
                    PointNode,
                    Ring)
from hypothesis import strategies

from tests.strategies import floats
from tests.utils import to_maybe

booleans = strategies.booleans()
sizes = strategies.integers(0, 65535)
points = strategies.builds(Point, floats, floats)
boxes = strategies.builds(Box, points, points)
maybe_points_nodes = to_maybe(strategies.builds(PointNode, floats, floats))
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings, maybe_rings_lists,
                          maybe_points_nodes, maybe_points_nodes, booleans)
