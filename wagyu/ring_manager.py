from typing import (List,
                    Optional)

from reprit.base import generate_repr

from .point import Point
from .point_node import PointNode
from .ring import Ring


class RingManager:
    __slots__ = ('children', 'all_nodes', 'hot_pixels', 'nodes', 'rings',
                 'storage', 'index')

    def __init__(self,
                 children: Optional[List[Optional[Ring]]] = None,
                 all_nodes: Optional[List[Optional[PointNode]]] = None,
                 hot_pixels: Optional[List[Point]] = None,
                 nodes: Optional[List[PointNode]] = None,
                 rings: Optional[List[Ring]] = None,
                 storage: Optional[List[PointNode]] = None,
                 index: int = 0) -> None:
        self.children = [] if children is None else children
        self.all_nodes = [] if all_nodes is None else all_nodes
        self.hot_pixels = [] if hot_pixels is None else hot_pixels
        self.nodes = [] if nodes is None else nodes
        self.rings = [] if rings is None else rings
        self.storage = [] if storage is None else storage
        self.index = index

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'RingManager') -> bool:
        return (self.children == other.children
                and self.all_nodes == other.all_nodes
                and self.hot_pixels == other.hot_pixels
                and self.nodes == other.nodes
                and self.rings == other.rings
                and self.storage == other.storage
                and self.index == other.index
                if isinstance(other, RingManager)
                else NotImplemented)
