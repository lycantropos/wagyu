from hypothesis import strategies

from tests.strategies import coordinates
from wagyu.point_node import PointNode

points_nodes = strategies.builds(PointNode, coordinates, coordinates)
