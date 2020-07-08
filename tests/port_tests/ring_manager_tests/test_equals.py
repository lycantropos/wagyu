from hypothesis import given

from tests.utils import (equivalence,
                         implication)
from wagyu.ring_manager import RingManager
from . import strategies


@given(strategies.ring_managers)
def test_reflexivity(ring_manager: RingManager) -> None:
    assert ring_manager == ring_manager


@given(strategies.ring_managers, strategies.ring_managers)
def test_symmetry(first_ring_manager: RingManager,
                  second_ring_manager: RingManager) -> None:
    assert equivalence(first_ring_manager == second_ring_manager,
                       second_ring_manager == first_ring_manager)


@given(strategies.ring_managers, strategies.ring_managers,
       strategies.ring_managers)
def test_transitivity(first_ring_manager: RingManager,
                      second_ring_manager: RingManager,
                      third_ring_manager: RingManager) -> None:
    assert implication(first_ring_manager == second_ring_manager
                       and second_ring_manager == third_ring_manager,
                       first_ring_manager == third_ring_manager)


@given(strategies.ring_managers, strategies.ring_managers)
def test_connection_with_inequality(first_ring_manager: RingManager,
                                    second_ring_manager: RingManager) -> None:
    assert equivalence(not first_ring_manager == second_ring_manager,
                       first_ring_manager != second_ring_manager)
