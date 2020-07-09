from typing import (Callable,
                    MutableSequence,
                    TypeVar)

Element = TypeVar('Element')


def bubble_sort(sequence: MutableSequence[Element],
                comparator: Callable[[Element, Element], bool],
                on_swap: Callable[[Element, Element], None]
                ) -> MutableSequence[Element]:
    if not sequence:
        return sequence
    result = sequence[:]
    while True:
        no_swaps = True
        for index in range(len(result) - 1):
            if not comparator(result[index], result[index + 1]):
                on_swap(result[index], result[index + 1])
                result[index], result[index + 1] = (result[index + 1],
                                                    result[index])
                if no_swaps:
                    no_swaps = False
        if no_swaps:
            return result
