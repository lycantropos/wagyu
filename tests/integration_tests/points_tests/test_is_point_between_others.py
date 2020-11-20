from _wagyu import is_point_between_others as bound
from hypothesis import given

from tests.integration_tests.utils import BoundPortedPointsPair
from tests.utils import equivalence
from wagyu.point import is_point_between_others as ported
from . import strategies


@given(strategies.points_pairs, strategies.points_pairs,
       strategies.points_pairs)
def test_basic(first_pair: BoundPortedPointsPair,
               second_pair: BoundPortedPointsPair,
               third_points_pair: BoundPortedPointsPair) -> None:
    bound_first, ported_first = first_pair
    bound_second, ported_second = second_pair
    bound_third, ported_third = third_points_pair

    assert equivalence(ported(ported_first, ported_second, ported_third),
                       bound(bound_first, bound_second, bound_third))
