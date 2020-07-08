from _wagyu import (Bound,
                    Box,
                    Edge,
                    Point,
                    PointNode,
                    Ring)
from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              trits)
from tests.utils import (bound_edges_sides,
                         bound_polygons_kinds,
                         to_maybe)

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
edges = strategies.builds(Edge, points, points)
integers_32 = strategies.integers(-2147483648, 2147483647)
edges_lists = strategies.lists(edges)
trits = trits
polygons_kinds = strategies.sampled_from(bound_polygons_kinds)
edges_sides = strategies.sampled_from(bound_edges_sides)
bounds = strategies.builds(Bound, edges_lists, points, maybe_rings, floats,
                           sizes, integers_32, integers_32, trits,
                           polygons_kinds, edges_sides)
