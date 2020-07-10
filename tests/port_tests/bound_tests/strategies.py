from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              non_negative_integers,
                              trits)
from tests.utils import (ported_edges_sides,
                         ported_polygons_kinds,
                         to_maybe)
from wagyu.bound import Bound
from wagyu.box import Box
from wagyu.edge import Edge
from wagyu.point import Point
from wagyu.point_node import PointNode
from wagyu.ring import Ring

booleans = strategies.booleans()
floats = floats
non_negative_integers = non_negative_integers
points = strategies.builds(Point, coordinates, coordinates)
boxes = strategies.builds(Box, points, points)
maybe_points_nodes = to_maybe(strategies.builds(PointNode, coordinates,
                                                coordinates))
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, non_negative_integers, maybe_rings_lists, maybe_points_nodes,
                          maybe_points_nodes, booleans)
edges = strategies.builds(Edge, points, points)
integers = strategies.integers()
edges_lists = strategies.lists(edges)
maybe_rings = to_maybe(rings)
polygons_kinds = strategies.sampled_from(ported_polygons_kinds)
edges_sides = strategies.sampled_from(ported_edges_sides)
bounds = strategies.builds(Bound, edges_lists, points, maybe_rings, floats,
                           non_negative_integers, integers, integers, trits,
                           polygons_kinds, edges_sides)
