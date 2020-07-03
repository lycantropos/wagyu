from _wagyu import PointNode
from hypothesis import strategies

from tests.strategies import coordinates

points_nodes = strategies.builds(PointNode, coordinates, coordinates)
