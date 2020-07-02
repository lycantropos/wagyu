from _wagyu import RingManager
from hypothesis import strategies

ring_managers = strategies.builds(RingManager)
