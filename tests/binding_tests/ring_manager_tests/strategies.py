from _wagyu import (Point,
                    Ring,
                    RingManager)
from hypothesis import strategies

from tests.strategies import (coordinates,
                              sizes)
from tests.utils import to_maybe

booleans = strategies.booleans()
sizes = sizes
points = strategies.builds(Point, coordinates, coordinates)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, sizes, maybe_rings_lists, booleans)
points_lists = strategies.lists(points)
rings_lists = strategies.lists(rings)
ring_managers = strategies.builds(RingManager, maybe_rings_lists, points_lists,
                                  sizes, rings_lists, sizes)
