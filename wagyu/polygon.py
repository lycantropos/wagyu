from collections import abc
from typing import (List,
                    Optional)

from .linear_ring import LinearRing
from .point_node import (PointNode,
                         point_node_to_point)
from .ring import Ring


class Polygon(abc.Sequence):
    __slots__ = 'linear_rings',

    def __init__(self, linear_rings: List[LinearRing]) -> None:
        self.linear_rings = linear_rings

    def __getitem__(self, index: int) -> LinearRing:
        return self.linear_rings[index]

    def __len__(self) -> int:
        return len(self.linear_rings)

    @classmethod
    def from_ring(cls, ring: Ring, reverse_output: bool) -> 'Polygon':
        return cls([point_node_to_linear_ring(ring.node, reverse_output)])

    def append(self, ring: Ring, reverse_output: bool) -> None:
        self.linear_rings.append(point_node_to_linear_ring(ring.node,
                                                           reverse_output))


Multipolygon = List[Polygon]


def point_node_to_linear_ring(node: PointNode,
                              reverse_output: bool) -> LinearRing:
    return LinearRing(list(map(point_node_to_point,
                               (iter if reverse_output else reversed)(node)))
                      # close the ring
                      + [point_node_to_point(node)])
