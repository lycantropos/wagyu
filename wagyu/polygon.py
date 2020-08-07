from collections import abc
from typing import (Iterable,
                    List,
                    Optional)

from reprit.base import generate_repr

from .linear_ring import LinearRing
from .point_node import (PointNode,
                         point_node_to_point)
from .ring import Ring


class Polygon(abc.Sequence):
    __slots__ = 'linear_rings',

    def __init__(self, linear_rings: List[LinearRing]) -> None:
        self.linear_rings = linear_rings

    __repr__ = generate_repr(__init__)

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


class Multipolygon(abc.Sequence):
    __slots__ = 'polygons',

    def __init__(self, polygons: List[Polygon]) -> None:
        self.polygons = polygons

    __repr__ = generate_repr(__init__)

    def __getitem__(self, index: int) -> Polygon:
        return self.polygons[index]

    def __len__(self) -> int:
        return len(self.polygons)

    @classmethod
    def from_rings(cls,
                   rings: List[Optional[Ring]],
                   reverse_output: bool) -> 'Multipolygon':
        return cls(list(rings_to_polygons(rings, reverse_output)))

    def extend(self,
               rings: List[Optional[Ring]],
               reverse_output: bool) -> None:
        self.polygons.extend(rings_to_polygons(rings, reverse_output))


def rings_to_polygons(rings: Iterable[Optional[Ring]],
                      reverse_output: bool) -> Iterable[Polygon]:
    for ring in rings:
        if ring is None:
            continue
        polygon = Polygon.from_ring(ring, reverse_output)
        yield polygon
        for child in ring.children:
            if child is None:
                continue
            polygon.append(child, reverse_output)
        for child in ring.children:
            if child is None:
                continue
            yield from rings_to_polygons(child.children, reverse_output)


def point_node_to_linear_ring(node: PointNode,
                              reverse_output: bool) -> LinearRing:
    return LinearRing(list(map(point_node_to_point,
                               (iter if reverse_output else reversed)(node)))
                      # close the ring
                      + [point_node_to_point(node)])
