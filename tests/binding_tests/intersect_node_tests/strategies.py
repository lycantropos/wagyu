from _wagyu import (Bound,
                    Box,
                    Edge,
                    IntersectNode,
                    Point,
                    Ring)
from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              integers_32,
                              sizes,
                              trits)
from tests.utils import (bound_edges_sides,
                         bound_polygons_kinds,
                         to_maybe)

booleans = strategies.booleans()
floats = floats
sizes = sizes
points = strategies.builds(Point, coordinates, coordinates)
points_lists = strategies.lists(points)
boxes = strategies.builds(Box, points, points)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings_lists, points_lists,
                          booleans)
edges = strategies.builds(Edge, points, points)
integers_32 = integers_32
edges_lists = strategies.lists(edges)
trits = trits
polygons_kinds = strategies.sampled_from(bound_polygons_kinds)
edges_sides = strategies.sampled_from(bound_edges_sides)
bounds = strategies.builds(Bound, edges_lists, sizes, sizes, points,
                           maybe_rings, floats, sizes, integers_32,
                           integers_32, trits, polygons_kinds, edges_sides)
intersect_nodes = strategies.builds(IntersectNode, bounds, bounds, points)
