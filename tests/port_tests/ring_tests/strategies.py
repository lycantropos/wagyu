from hypothesis import strategies

from tests.strategies import (coordinates,
                              floats,
                              non_negative_integers)
from tests.utils import to_maybe
from wagyu.box import Box
from wagyu.point import Point
from wagyu.ring import Ring

booleans = strategies.booleans()
floats = floats
non_negative_integers = non_negative_integers
points = strategies.builds(Point, coordinates, coordinates)
points_lists = strategies.lists(points)
boxes = strategies.builds(Box, points, points)
maybe_rings = to_maybe(strategies.deferred(lambda: rings))
maybe_rings_lists = strategies.lists(maybe_rings)
rings = strategies.builds(Ring, non_negative_integers, maybe_rings_lists,
                          points_lists, booleans)
