from hypothesis import strategies

from wagyu.bound import Bound

bounds = strategies.builds(Bound)
