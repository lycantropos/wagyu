from reprit.base import generate_repr

from .box import Box
from .enums import (FillKind,
                    OperationKind,
                    PolygonKind)
from .linear_ring import LinearRing
from .local_minimum import LocalMinimumList
from .point import Point
from .polygon import (Multipolygon,
                      Polygon)
from .ring_manager import RingManager


class Wagyu:
    __slots__ = 'minimums', 'reverse_output'

    def __init__(self,
                 reverse_output: bool = False) -> None:
        self.minimums = LocalMinimumList()
        self.reverse_output = reverse_output

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Wagyu') -> bool:
        return (self.minimums == other.minimums
                and self.reverse_output is other.reverse_output
                if isinstance(other, Wagyu)
                else NotImplemented)

    @property
    def bounds(self) -> Box:
        minimum, maximum = Point(0, 0), Point(0, 0)
        if not self.minimums:
            return Box(minimum, maximum)
        first_set = False
        for local_minimum in self.minimums:
            left_bound = local_minimum.left_bound
            if left_bound.edges:
                if not first_set:
                    minimum = left_bound.edges[0].top
                    maximum = left_bound.edges[-1].bottom
                    first_set = True
                else:
                    minimum.x = min(minimum.x, left_bound.edges[-1].top.x)
                    minimum.y = min(minimum.y, left_bound.edges[0].top.y)
                    maximum.x = max(maximum.x, left_bound.edges[-1].top.x)
                    maximum.y = max(maximum.y, left_bound.edges[-1].bottom.y)
                for edge in left_bound.edges:
                    minimum.x = min(minimum.x, edge.bottom.x)
                    maximum.x = max(maximum.x, edge.bottom.x)
            right_bound = local_minimum.right_bound
            if right_bound.edges:
                if not first_set:
                    minimum = right_bound.edges[0].top
                    maximum = right_bound.edges[-1].bottom
                    first_set = True
                else:
                    minimum.x = min(minimum.x, right_bound.edges[-1].top.x)
                    minimum.y = min(minimum.y, right_bound.edges[0].top.y)
                    maximum.x = max(maximum.x, right_bound.edges[-1].top.x)
                    maximum.y = max(maximum.y, right_bound.edges[-1].bottom.y)
                for edge in right_bound.edges:
                    minimum.x = min(minimum.x, edge.bottom.x)
                    maximum.x = max(maximum.x, edge.bottom.x)
        return Box(minimum, maximum)

    def add_linear_ring(self,
                        ring: LinearRing,
                        polygon_kind: PolygonKind) -> bool:
        return self.minimums.add_linear_ring(ring, polygon_kind)

    def add_polygon(self,
                    polygon: Polygon,
                    polygon_kind: PolygonKind) -> bool:
        result = False
        for linear_ring in polygon:
            if self.add_linear_ring(linear_ring, polygon_kind) and not result:
                result = True
        return result

    def clear(self) -> None:
        self.minimums.clear()

    def execute(self,
                operation_kind: OperationKind,
                subject_fill_type: FillKind,
                clip_fill_type: FillKind) -> Multipolygon:
        if not self.minimums:
            return Multipolygon([])
        manager = RingManager()
        manager.build_hot_pixels(self.minimums)
        manager.execute_vatti(self.minimums, operation_kind, subject_fill_type,
                              clip_fill_type)
        manager.correct_topology()
        return manager.build_result(self.reverse_output)

    def intersect(self,
                  subject_fill_type: FillKind = FillKind.EVEN_ODD,
                  clip_fill_type: FillKind = FillKind.EVEN_ODD
                  ) -> Multipolygon:
        return self.execute(OperationKind.INTERSECTION, subject_fill_type,
                            clip_fill_type)

    def subtract(self,
                 subject_fill_type: FillKind = FillKind.EVEN_ODD,
                 clip_fill_type: FillKind = FillKind.EVEN_ODD) -> Multipolygon:
        return self.execute(OperationKind.DIFFERENCE, subject_fill_type,
                            clip_fill_type)

    def symmetric_subtract(self,
                           subject_fill_type: FillKind = FillKind.EVEN_ODD,
                           clip_fill_type: FillKind = FillKind.EVEN_ODD
                           ) -> Multipolygon:
        return self.execute(OperationKind.XOR, subject_fill_type,
                            clip_fill_type)

    def unite(self,
              subject_fill_type: FillKind = FillKind.EVEN_ODD,
              clip_fill_type: FillKind = FillKind.EVEN_ODD) -> Multipolygon:
        return self.execute(OperationKind.UNION, subject_fill_type,
                            clip_fill_type)
