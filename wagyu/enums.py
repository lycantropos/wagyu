from enum import (IntEnum,
                  unique)


@unique
class EdgeSide(IntEnum):
    LEFT = 0
    RIGHT = 1


@unique
class FillKind(IntEnum):
    EVEN_ODD = 0
    NON_ZERO = 1
    POSITIVE = 2
    NEGATIVE = 3


@unique
class OperationKind(IntEnum):
    INTERSECTION = 0
    UNION = 1
    DIFFERENCE = 2
    XOR = 3


@unique
class PolygonKind(IntEnum):
    SUBJECT = 0
    CLIP = 1
