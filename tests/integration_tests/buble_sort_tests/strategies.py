from hypothesis import strategies

from tests.strategies import coordinates

unique_comparables_lists_with_comparators = strategies.tuples(
        strategies.lists(coordinates,
                         unique=True),
        # we should be able to use ``operator`` module members
        # once https://github.com/pybind/pybind11/pull/1413 gets merged
        strategies.sampled_from([lambda x, y: x < y, lambda x, y: x > y]))
