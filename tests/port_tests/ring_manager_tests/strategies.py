from hypothesis import strategies

from tests.strategies import coordinates
from tests.utils import to_maybe
from wagyu.point import Point
from wagyu.point_node import PointNode
from wagyu.ring import Ring
from wagyu.ring_manager import RingManager

booleans = strategies.booleans()
sizes = strategies.integers(0)
points = strategies.builds(Point, coordinates, coordinates)
points_nodes = strategies.builds(PointNode, coordinates, coordinates)
maybe_points_nodes = to_maybe(points_nodes)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings_lists, maybe_points_nodes,
                          maybe_points_nodes, booleans)
points_lists = strategies.lists(points)
points_nodes_lists = strategies.lists(points_nodes)
maybe_points_nodes_lists = strategies.lists(maybe_points_nodes)
rings_lists = strategies.lists(rings)
ring_managers = strategies.builds(RingManager, maybe_rings_lists,
                                  maybe_points_nodes_lists, points_lists,
                                  points_nodes_lists, rings_lists,
                                  points_nodes_lists, sizes)
