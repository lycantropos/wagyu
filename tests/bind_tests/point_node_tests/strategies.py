from _wagyu import PointNode
from hypothesis import strategies

from tests.strategies import floats

points_nodes = strategies.builds(PointNode, floats, floats)
