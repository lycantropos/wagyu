from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.box import Box
from . import strategies


@given(strategies.boxes)
def test_reflexivity(box: Box) -> None:
    assert box == box


@given(strategies.boxes, strategies.boxes)
def test_symmetry(first_box: Box,
                  second_box: Box) -> None:
    assert equivalence(first_box == second_box,
                       second_box == first_box)


@given(strategies.boxes, strategies.boxes,
       strategies.boxes)
def test_transitivity(first_box: Box,
                      second_box: Box,
                      third_box: Box) -> None:
    assert implication(first_box == second_box
                       and second_box == third_box,
                       first_box == third_box)


@given(strategies.boxes, strategies.boxes)
def test_connection_with_inequality(first_box: Box,
                                    second_box: Box) -> None:
    assert equivalence(not first_box == second_box,
                       first_box != second_box)
