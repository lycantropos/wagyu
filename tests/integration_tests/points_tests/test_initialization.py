from hypothesis import given

from tests.binding_tests.utils import BoundPoint
from tests.integration_tests.utils import are_bound_ported_points_equal
from tests.port_tests.utils import PortedPoint
from . import strategies


@given(strategies.coordinates, strategies.coordinates)
def test_basic(x: float, y: float) -> None:
    bound, ported = BoundPoint(x, y), PortedPoint(x, y)

    assert are_bound_ported_points_equal(bound, ported)
