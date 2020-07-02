from _wagyu import (Box,
                    Point,
                    PointNode,
                    RingManager)
from hypothesis import strategies

from tests.strategies import floats
from tests.utils import to_maybe

booleans = strategies.booleans()
sizes = strategies.integers(0, 65535)
points = strategies.builds(Point, floats, floats)
boxes = strategies.builds(Box, points, points)
maybe_points_nodes = to_maybe(strategies.builds(PointNode, floats, floats))
maybe_ring_managers = to_maybe(strategies.deferred(lambda: ring_managers))
maybe_ring_managers_lists = strategies.lists(maybe_ring_managers)
ring_managers = strategies.builds(RingManager)
