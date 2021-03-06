from functools import partial
from typing import (Callable,
                    List,
                    Tuple)

from _wagyu import bubble_sort as bound
from hypothesis import given

from wagyu.bubble_sort import bubble_sort as ported
from wagyu.hints import Domain
from . import strategies


@given(strategies.unique_comparables_lists_with_comparators)
def test_basic(comparables_with_comparator
               : Tuple[List[Domain], Callable[[Domain, Domain], bool]]
               ) -> None:
    comparables, comparator = comparables_with_comparator

    def on_swap(elements: List[Tuple[Domain, Domain]],
                left: Domain,
                right: Domain) -> None:
        elements.append((left, right))

    bound_swaps, ported_swaps = [], []
    assert (bound(comparables, comparator, partial(on_swap, bound_swaps))
            == ported(comparables, comparator, partial(on_swap, ported_swaps)))
    assert bound_swaps == ported_swaps
