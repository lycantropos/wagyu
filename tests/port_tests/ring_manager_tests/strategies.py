from hypothesis import strategies

from tests.strategies import (coordinates,
                              non_negative_integers)
from tests.utils import to_maybe
from wagyu.point import Point
from wagyu.ring import Ring
from wagyu.ring_manager import RingManager

booleans = strategies.booleans()
non_negative_integers = non_negative_integers
points = strategies.builds(Point, coordinates, coordinates)
points_lists = strategies.lists(points)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, non_negative_integers, maybe_rings_lists,
                          points_lists, booleans)
rings_lists = strategies.lists(rings)
ring_managers = strategies.builds(RingManager, maybe_rings_lists, points_lists,
                                  non_negative_integers, rings_lists,
                                  non_negative_integers)
