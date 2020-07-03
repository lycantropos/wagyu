from _wagyu import Multipolygon
from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.multipolygons)
def test_reflexivity(multipolygon: Multipolygon) -> None:
    assert multipolygon == multipolygon


@given(strategies.multipolygons, strategies.multipolygons)
def test_symmetry(first_multipolygon: Multipolygon, second_multipolygon: Multipolygon) -> None:
    assert equivalence(first_multipolygon == second_multipolygon,
                       second_multipolygon == first_multipolygon)


@given(strategies.multipolygons, strategies.multipolygons,
       strategies.multipolygons)
def test_transitivity(first_multipolygon: Multipolygon,
                      second_multipolygon: Multipolygon,
                      third_multipolygon: Multipolygon) -> None:
    assert implication(first_multipolygon == second_multipolygon
                       and second_multipolygon == third_multipolygon,
                       first_multipolygon == third_multipolygon)


@given(strategies.multipolygons, strategies.multipolygons)
def test_connection_with_inequality(first_multipolygon: Multipolygon,
                                    second_multipolygon: Multipolygon) -> None:
    assert equivalence(not first_multipolygon == second_multipolygon,
                       first_multipolygon != second_multipolygon)
