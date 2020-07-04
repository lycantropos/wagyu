from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats)
from tests.utils import to_maybe
from wagyu.box import Box
from wagyu.point import Point
from wagyu.point_node import PointNode
from wagyu.ring import Ring

booleans = strategies.booleans()
floats = floats
sizes = strategies.integers(0, 65535)
points = strategies.builds(Point, coordinates, coordinates)
boxes = strategies.builds(Box, points, points)
maybe_points_nodes = to_maybe(strategies.builds(PointNode, coordinates,
                                                coordinates))
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings_lists, maybe_points_nodes,
                          maybe_points_nodes, booleans)
